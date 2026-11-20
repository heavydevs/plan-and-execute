#!/usr/bin/env python3
"""Offline contracts for role fit, quota families, explicit overrides and floors."""
from __future__ import annotations
import copy
import json
import tempfile
import unittest
from pathlib import Path

import availability
import planctl
import routing_config
import routingctl
import run_isolated as runner
import workload_routing as wr
from self_test import sample_spec


def config():
    cfg = routingctl.apply_catalog(planctl.default_config()) if hasattr(routingctl, 'apply_catalog') else planctl.default_config()
    cfg = routing_config.merge(cfg, routing_config.EXTRA_DEFAULTS)
    cfg['provider_order'] = ['antigravity', 'claude', 'codex']
    cfg.update(wr.antigravity_preset(['gemini-3.8-flash-medium', 'claude-opus-5-5-high']))
    profiles = cfg['workload_routing']['profiles']
    # Same requested capability, two independent family quotas on one host.
    profiles['agy-flash-monitor']['workloads'].append('implementation')
    cfg['workload_routing']['routes']['implementation'].insert(0, 'agy-flash-monitor')
    return cfg


class WorkloadTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cfg = config()
        self.task = {'id': '001', 'provider': 'auto', 'workload': 'implementation',
                     'model_tier': 'standard', 'reasoning_effort': 'medium', 'functional_failures': 0}
        self.intent = {'provider': 'claude', 'tier': 'standard', 'model': 'old', 'effort': 'medium'}

    def select(self, **kwargs):
        return availability.select(self.root, self.task, self.cfg, self.intent,
            kwargs.get('override'), 'implementation', kwargs.get('visited', set()),
            kwargs.get('available', lambda _: True), runner.clamp_effort, now=100)

    def test_family_quota_fallback_same_host_no_floor_change(self):
        first = self.select()
        self.assertEqual(first['route_profile'], 'agy-flash-monitor')
        availability.unavailable(self.root, '001', 'implementation', first, 'quota', self.cfg, now=100)
        second = self.select(visited={wr.identity(first)})
        self.assertEqual(second['route_profile'], 'agy-claude-intermediate')
        self.assertEqual(second['provider'], 'antigravity')
        self.assertEqual(second['tier'], 'standard')
        self.assertEqual(second['requested_effort'], 'medium')
        self.assertEqual(self.task['functional_failures'], 0)
        state = availability.read(self.root, '001')
        self.assertIn('pool/antigravity-gemini', state['cooldowns'])
        self.assertNotIn('antigravity', state['cooldowns'])

    def test_auth_blocks_host_not_other_providers(self):
        first = self.select()
        availability.unavailable(self.root, '001', 'implementation', first, 'authentication', self.cfg, now=100)
        self.assertEqual(self.select()['provider'], 'claude')

    def test_capacity_blocks_model_not_whole_family(self):
        first = self.select()
        availability.unavailable(self.root, '001', 'implementation', first, 'capacity', self.cfg, now=100)
        self.assertTrue(next(iter(availability.read(self.root,'001')['cooldowns'])).startswith('model/antigravity/'))
        self.assertEqual(self.select()['route_profile'], 'agy-claude-intermediate')

    def test_legacy_provider_cooldown_remains_conservative(self):
        availability._save(self.root,'001', {'version':1,'cooldowns':{'antigravity':{'until':500,'reason':'quota'}},'phases':{},'events':[]})
        self.assertEqual(self.select()['provider'], 'claude')

    def test_strong_never_uses_intermediate_profile(self):
        self.intent.update(tier='strong', effort='high')
        route = self.select()
        self.assertNotEqual(route.get('route_profile'), 'agy-claude-intermediate')
        self.assertEqual(route['tier'], 'strong')

    def test_xhigh_never_silently_clamps_profile(self):
        self.intent['effort']='xhigh'
        self.assertNotIn('route_profile', self.select())

    def test_explicit_provider_and_no_fallback_are_authoritative(self):
        self.assertEqual(self.select(override='codex')['provider'], 'codex')
        self.task['provider']='claude';self.task['allow_provider_fallback']=False
        self.assertEqual(self.select()['provider'],'claude')
        with self.assertRaises(availability.AvailabilityPaused): self.select(available=lambda _:False)

    def test_missing_cli_blocks_all_host_variants(self):
        self.assertEqual(self.select(available=lambda p:p!='antigravity')['provider'],'claude')
        self.assertIn('antigravity', availability.read(self.root,'001')['cooldowns'])

    def test_shared_pool_across_profiles(self):
        self.cfg['workload_routing']['profiles']['agy-claude-intermediate']['quota_pool']='antigravity-gemini'
        first=self.select();availability.unavailable(self.root,'001','implementation',first,'quota',self.cfg,now=100)
        self.assertEqual(self.select()['provider'],'claude')

    def test_task_workload_retained_and_rejected_if_unknown(self):
        raw=sample_spec()['tasks'][0];raw['workload']='frontend_design'
        task=planctl.normalize_task(raw,0,{'R001','R002'})
        self.assertEqual(task['workload'],'frontend_design')
        raw['workload']='magic'
        with self.assertRaises(planctl.PlanError):planctl.normalize_task(raw,0,{'R001','R002'})

    def test_observed_inventory_and_cap_validation(self):
        routing_config.validate(self.cfg)
        for key,value in [('model','invented-model'),('max_tier','max'),('quota_pool','../escape')]:
            cfg=copy.deepcopy(self.cfg);cfg['workload_routing']['profiles']['agy-claude-intermediate'][key]=value
            with self.assertRaises(routing_config.ConfigError):routing_config.validate(cfg)

    def test_workload_affinity_is_not_a_generic_intelligence_claim(self):
        self.task['workload']='frontend_design'
        self.assertEqual(self.select()['route_profile'],'agy-claude-intermediate')
        self.task['workload']='log_monitoring'
        self.assertEqual(self.select()['route_profile'],'agy-flash-monitor')
        self.assertEqual(routingctl.minimum_route(['log_monitoring']),{'tier':'tool','effort':'none'})
        self.assertEqual(routingctl.minimum_route(['log_diagnosis'])['tier'],'economy')
        self.assertEqual(routingctl.minimum_route(['frontend_design','cross_cutting_risk'])['tier'],'strong')

    def test_embedded_model_effort_not_duplicated_in_argv(self):
        route=self.select()
        command=runner.build_worker_command('antigravity',route,self.cfg,'prompt',self.root/'result.json')
        self.assertIn('gemini-3.8-flash-medium',command)
        self.assertNotIn('--effort',command)

    def test_snapshot_cannot_replace_profile_model_or_quota(self):
        route=self.select();cfg={**self.cfg,'model_resolution':'snapshot'}
        actual=runner.resolve_snapshot_route(self.root,self.task,route,cfg,{'antigravity':{'standard':'wrong'}})
        self.assertEqual(actual,route)

    def test_presets_never_invent_missing_model(self):
        self.assertEqual(wr.antigravity_preset([])['workload_routing']['profiles'],{})
        self.assertEqual(wr.inventory_models({'models':[{'id':'gemini-3.8-flash-medium'}]}),['gemini-3.8-flash-medium'])
        with self.assertRaises(wr.WorkloadError): wr.inventory_models('some prose')

    def test_gemini4_preset_puts_neon_first_at_standard(self):
        # Map 2026-11-20-v11: Neon serves standard..strong ahead of Hydrogen; Hydrogen keeps economy and is the
        # standard fallback; Flash only monitors; Antigravity Claude stays capped at advanced; no Carbon/Argon.
        listed = [f'gemini-4-{family}-{effort}' for family in ('neon', 'hydrogen') for effort in ('low', 'medium', 'high', 'xhigh')]
        listed += ['gemini-4-argon-high', 'gemini-4-carbon-high', 'gemini-3.8-flash-medium', 'claude-opus-5-5-high']
        section = wr.antigravity_preset(listed)['workload_routing']
        wr.validate(section, routing_config.PROVIDERS)
        profiles = section['profiles']
        self.assertFalse(any('carbon' in p['model'] or 'argon' in p['model'] for p in profiles.values()))
        self.assertEqual((profiles['agy-neon-low']['min_tier'], profiles['agy-neon-xhigh']['max_tier']), ('standard', 'strong'))
        self.assertEqual((profiles['agy-hydrogen-low']['min_tier'], profiles['agy-hydrogen-xhigh']['max_tier']), ('economy', 'standard'))
        self.assertEqual(profiles['agy-claude-intermediate']['max_tier'], 'advanced')
        self.assertEqual(section['routes']['log_monitoring'], ['agy-flash-monitor'])
        cfg = routing_config.merge(planctl.default_config(), routing_config.EXTRA_DEFAULTS)
        cfg['provider_order'] = ['antigravity', 'codex', 'claude']
        cfg['workload_routing'] = section
        clamp = lambda provider_cfg, tier, effort: effort
        def first(tier, effort):
            task = {'provider': 'auto', 'workload': 'implementation', 'model_tier': tier}
            return wr.candidates(task, cfg, ['antigravity', 'codex', 'claude'], tier, effort, clamp)[0]['route_profile']
        self.assertEqual(first('economy', 'low'), 'agy-hydrogen-low')
        self.assertEqual(first('standard', 'low'), 'agy-neon-low')
        self.assertEqual(first('standard', 'medium'), 'agy-neon-medium')
        self.assertEqual(first('standard', 'high'), 'agy-neon-high')
        self.assertEqual(first('advanced', 'high'), 'agy-neon-high')
        self.assertEqual(first('strong', 'xhigh'), 'agy-neon-xhigh')
        task = {'provider': 'auto', 'workload': 'implementation', 'model_tier': 'standard'}
        order = [r.get('route_profile') for r in wr.candidates(task, cfg, ['antigravity', 'codex', 'claude'], 'standard', 'medium', clamp)]
        # Hydrogen medium is the cheaper same-effort fallback after the Neon variants, before the Claude profile.
        self.assertLess(order.index('agy-neon-xhigh'), order.index('agy-hydrogen-medium'))
        self.assertLess(order.index('agy-hydrogen-xhigh'), order.index('agy-claude-intermediate'))
        # Max is not an Antigravity tier: the overlay offers no profile there.
        self.assertFalse([r for r in wr.candidates({**task, 'model_tier': 'max'}, cfg, ['antigravity'], 'max', 'xhigh', clamp)
                          if r.get('route_profile')])

    def test_absent_section_preserves_old_routes_and_keys(self):
        self.cfg.pop('workload_routing')
        first=self.select()
        self.assertEqual(first['model'],self.cfg['antigravity']['models']['standard'])
        self.assertNotIn('route_profile',first)
        availability.unavailable(self.root,'001','implementation',first,'quota',self.cfg,now=100)
        self.assertIn('antigravity',availability.read(self.root,'001')['cooldowns'])


if __name__=='__main__': unittest.main()
