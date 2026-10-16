"""Retry only E009's two failed v10 contracts, preserving every completed stage.

SCGBinner owns an independent locked CPU Conda stack. COMEBin keeps its accepted
numerical recipe but calls complete CheckM in a separate owned Conda environment.
No source DNA acquisition/catalog, mapping, assembler, evaluator, other tool,
community fit or benchmark score is scheduled here. Old attempts remain read-only.
"""
import json
import os
from pathlib import Path
import shlex
import shutil
import sys

from e009_common import binding, extract, write_json
from e009_native import patch_scgbinner

EXP='experiments/E009-competitive-benchmark'


def verify_reused_inputs(review, previous, reference, bams=None):
    """Verify small accepted receipts and exact tiny ordered BAM/reference bytes.

    Large source DNA, source catalogs and environments are not rescanned. Explicit
    local BAM overrides test Mac native readers; they never grant Linux validation.
    Return the ordered existing BAM paths; missing/drifting evidence fails closed.
    """
    previous=Path(previous)
    for name,expected in review['required_retained_evidence'].items():
        if binding(previous/name)!=expected:raise ValueError('Retained v10 evidence changed: '+name)
    status=json.loads((previous/'native-contract-status.json').read_text())
    if any(status[t]['status']!='passed' for t in review['accepted_tools']):
        raise ValueError('Accepted v10 tool status differs')
    if binding(reference)!=review['fixture']['reference']:raise ValueError('Retained fixture reference changed')
    records=bams if bams is not None else review['fixture']['ordered_bams']
    if len(records)!=2 or len({r['path'] for r in records})!=2:raise ValueError('Two distinct ordered retained BAMs required')
    for record in records:
        if binding(record['path'])!=record['file']:raise ValueError('Retained ordered BAM bytes changed')
    return [Path(r['path']) for r in records]


def verify_conda_identity(prefix, lock):
    """Check the exact installed Conda name/version/build set, without file-tree hashing.

    Payload SHA256/MD5 verification occurs before offline installation. Python
    inventory/origin/native probes separately establish the executed import path.
    The SCGBinner stack, including CPU Torch, is entirely Conda-owned.
    """
    actual={}
    for path in (Path(prefix)/'conda-meta').glob('*.json'):
        r=json.loads(path.read_text())
        if r['name'] in actual:raise ValueError('Duplicate Conda package record')
        actual[r['name']]=(r['version'],r['build'])
    expected={p['name']:(p['version'],p['build']) for p in lock['packages']}
    if actual!=expected:raise ValueError('Installed Conda package identity set differs from locked recipe')
    return {'prefix':str(prefix),'packages':len(actual),'identity_set_matches':True,
            'scope':'exact Conda name/version/build records; payloads verified preinstall, no blanket postinstall file hashes'}


def checkm_wrapper(path, python, script, cache_root, native_wrappers=None):
    """Invoke owned CheckM with its own libraries and isolated lexical Python.

    A COMEBin worker inherits its numerical LD_LIBRARY_PATH; explicitly replace it
    for this different CheckM stack. Never use the old E001 console or a borrowed
    checkm.test namespace. Preserve argv and the job's no-bytecode-write policy.
    """
    python,script=Path(python),Path(script)
    argv=[python,'-I','-B','-X','pycache_prefix='+str(cache_root),script]
    own_bin=python.parent
    native_path=(str(native_wrappers)+':' if native_wrappers else '')+str(own_bin)
    Path(path).write_text('#!/bin/sh\nunset PYTHONPATH PYTHONHOME PYTHONUSERBASE\n'
        'export PYTHONNOUSERSITE=1\nexport PATH='+shlex.quote(native_path)+':"$PATH"\nexport LD_LIBRARY_PATH='+shlex.quote(str(python.parent.parent/'lib'))+'\n'
        'exec '+' '.join(shlex.quote(str(a)) for a in argv)+' "$@"\n')
    Path(path).chmod(0o755)
    return binding(path)


def retry(args, attempt, bundle, env, stage, deadline, limits, local=None):
    """Run fresh corrected installs and only the two remaining tiny native contracts.

    Parent owner driver already owns the allocation affinity, isolation, total
    clock, resource/stall monitoring and collection. A failure skips its dependent
    contract; the other independently owned failed path may still be checked.
    """
    from e009_owner import restored_runtime,tool_environment,python_wrapper
    review=json.loads((bundle/EXP/'linux-preflight-v10.json').read_text())
    recipes=json.loads((bundle/EXP/'failed-paths-lock.json').read_text())
    native=json.loads((bundle/EXP/'native-lock.json').read_text())
    if not local and args.root!=Path('/work/Home/dl_binner/e009'):
        raise ValueError('Owner root differs from frozen E009 Home root')
    reference=bundle/'input/assembly.fna'
    previous=Path(local['prior_attempt']) if local else Path(review['attempt'])
    print('DLBINNER RETRY verifying small retained receipts and ordered tiny BAMs',flush=True)
    bams=verify_reused_inputs(review,previous,reference,local.get('ordered_bams') if local else None)
    write_json(attempt/'reused-v10-evidence.json',{'prior_attempt':str(previous),
        'accepted_tools':review['accepted_tools'],'accepted_stages':review['accepted_stages'],
        'reference':binding(reference),'ordered_bams':[{'path':str(p),'file':binding(p)} for p in bams],
        'scientific_execution_admitted':False,'scope':'completed stages reused, not scheduled'})
    utility=Path(local['utility_prefix']) if local else Path(review['utility_prefix'])
    if not (utility/'bin/bedtools').is_file():raise ValueError('Retained utility bedtools missing; preserve v10 and return failure')
    cache=args.root/'cache'/('failed-paths-v4-'+attempt.name);cache.mkdir(parents=True)
    sources={}
    for tool,name in [('scgbinner','SCGBinner'),('comebin','COMEBin')]:
        spec=native['sources'][name]
        source_archive=(Path(local['source_archives'][name]) if local else
            args.root/'cache/sources'/(name+'-'+spec['sha256'][:12]+'.tar.gz'))
        if binding(source_archive)!={k:spec[k] for k in ('bytes','sha256')}:
            raise ValueError('Acquired pinned source changed: '+name)
        print('DLBINNER RETRY reuse pinned acquired source '+name,flush=True)
        target=attempt/'sources'/name;extract(source_archive,target,strip_root=True);sources[tool]=target
    patch=patch_scgbinner(sources['scgbinner'],native['scgbinner_modification']['before_sha256'])
    if patch['after']!=native['scgbinner_modification']['after']:raise ValueError('Accepted SCGBinner dtype patch differs')
    write_json(attempt/'scgbinner-modification.json',patch)
    results={t:{'status':'passed','reused_from':str(previous),'executed_this_attempt':False}
             for t in review['accepted_tools']}
    prefixes={}
    if not local:
        if shutil.disk_usage(args.root).free<10_000_000_000:raise ValueError('Need >=10 GB free Home for the two owned runtimes/cache/evidence')
        bootstrap=attempt/'bootstrap';extract(bundle/'payload/micromamba-linux.tar.bz2',bootstrap)
        mamba=bootstrap/'bin/micromamba'
    for tool in ['scgbinner','comebin']:
        try:
            kind='scgbinner' if tool=='scgbinner' else 'checkm'
            lock=recipes[kind]
            if local:
                prefix=Path(local[kind+'_prefix'])
                # Mac identity replaces only the platform-specific install; all
                # production prefix/probe/wrapper/native reader paths run below.
                own_lock=json.loads(Path(local[kind+'_lock']).read_text())
            else:
                prefix=args.root/'envs'/(kind+'-cpu-v4-'+attempt.name)
                if prefix.exists():raise ValueError('Corrected runtime prefix must be fresh')
                lockfile=attempt/(kind+'-conda-lock.json');write_json(lockfile,lock)
                explicit=attempt/(kind+'-conda-explicit.txt')
                stage([sys.executable,'-I','-B',bundle/'scripts/e009_worker.py','acquire-conda',
                    '--lock',lockfile,'--destination',cache/'conda','--explicit',explicit],kind+'-locked-acquisition')
                setupenv=dict(env,MAMBA_ROOT_PREFIX=str(args.root/'mamba'),CONDA_PKGS_DIRS=str(cache/'conda-cache'))
                setupenv.pop('LD_LIBRARY_PATH',None)
                stage([mamba,'--no-rc','create','-y','--offline','--always-copy','-p',prefix,'--file',explicit],kind+'-owned-conda-install',setupenv)
                own_lock=lock
            write_json(attempt/(kind+'-conda-identity.json'),verify_conda_identity(prefix,own_lock))
            prefixes[kind]=str(prefix)
            required=dict(recipes['required_distributions'][kind])
            if local:
                # Both platforms use the all-Conda CPU Torch release.
                if kind=='scgbinner':required['torch']='2.0.0.post104'
            expected=attempt/(kind+'-required-inventory.json');write_json(expected,required)
            toolenv=dict(env,LD_LIBRARY_PATH=str(prefix/'lib'),PATH=str(prefix/'bin')+':'+str(utility/'bin')+':'+env.get('PATH',''))
            for key in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):toolenv[key]='1'
            modules=['numpy','torch','pandas','scipy','sklearn'] if kind=='scgbinner' else ['numpy','scipy','matplotlib','pysam','dendropy','checkm.test.test_ecoli']
            stage([prefix/'bin/python','-I','-B',bundle/'scripts/e009_native.py','--inventory-prefix',prefix,
                   '--required-distributions',expected,'--modules',*modules],kind+'-owned-isolated-probe',toolenv)
            if kind=='checkm':
                # A complete CheckM package also needs working native entry points;
                # help/version checks run no lineage placement or community fit.
                commands=[('hmmsearch',['-h']),('prodigal',['-v']),('pplacer',['--help'])]
                if not local:
                    for binary,flags in commands:
                        stage([prefix/'bin'/binary,*flags],'checkm-owned-'+binary+'-entry',toolenv)
                write_json(attempt/'checkm-native-entry-scope.json',{'owned_prefix':str(prefix),
                    'commands':commands,'executed':not bool(local),
                    'scope':'Linux owned native entry points only; no placement/lineage fit. Mac validation lacks the pinned Linux pplacer package.'})
            if tool=='scgbinner':
                python=prefix/'bin/python'
            else:
                checkm_python=prefix/'bin/python'
                if local:
                    python=Path(local['comebin_python'])
                else:
                    base,inv=restored_runtime(bundle/EXP/'linux-runtime-recovery-v8.json',attempt,env,stage)
                    execution=args.root/'envs'/('comebin-source-v4-'+attempt.name)
                    links=tool_environment(base,inv,execution,stage)
                    write_json(attempt/'comebin-dependency-links.json',{'prefix':str(execution),'base_prefix':str(base),'links':links})
                    python=execution/'bin/python';toolenv=dict(env,LD_LIBRARY_PATH=str(base/'lib'))
                    complete={d['name']:d['version'] for d in inv['distributions']
                        if not d['name'].lower().startswith(('dl-binner','comebin','scgbinner','semibin','completebin','metacat'))}
                    expected_main=attempt/'comebin-expected-inventory.json';write_json(expected_main,complete)
                    stage([python,'-I','-B',bundle/'scripts/e009_native.py','--inventory-prefix',execution,
                        '--dependency-prefix',base,'--expected-distributions',expected_main,
                        '--forbidden-prefix',json.loads((bundle/EXP/'linux-runtime-recovery-v8.json').read_text())['snapshot']['source_prefix'],
                        '--modules','numpy','torch','pandas','scipy','sklearn'],'comebin-new-binding-probe',toolenv)
                wrapperdir=attempt/'wrappers';wrapperdir.mkdir()
                write_json(attempt/'checkm-wrapper-bound.json',{'owned_prefix':str(prefix),
                    'wrapper':checkm_wrapper(wrapperdir/'checkm',checkm_python,prefix/'bin/checkm',env['E009_SOURCE_CACHE_ROOT'],attempt/'comebin-wrappers')})
                toolenv.update(PATH=str(wrapperdir)+':'+str(utility/'bin')+':'+env.get('PATH',''),CHECKM_DATA_PATH=review['checkm_data'])
            for key in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):toolenv[key]='1'
            # Existing HMM master accounting is available without altering any
            # installed binary or accepted utility environment.
            wrappers=attempt/(tool+'-wrappers');wrappers.mkdir()
            hmm_python=checkm_python if tool=='comebin' else python
            hmm_native=prefix/'bin/hmmsearch' if tool=='comebin' and not local else utility/'bin/hmmsearch'
            python_wrapper(wrappers/'hmmsearch',hmm_python,bundle/'scripts/e009_hmm.py',['--native',hmm_native,'--'],env)
            toolenv['PATH']=str(wrappers)+':'+toolenv['PATH'];toolenv['E009_HMM_AUDIT']=str(attempt/(tool+'-hmm-budget.jsonl'))
            stage([python,'-I','-B',bundle/'scripts/e009_worker.py','tool-contract','--tool',tool,'--source',sources[tool],
                '--inputs',bundle/'input','--bams',*bams,'--output',attempt/(tool+'-contract'),'--db',attempt/'unused-database',
                '--threads',str(args.allocated_vcpus),
                *(['--reused-help',previous/'comebin-contract/native-full-import-help.log'] if tool=='comebin' else [])],tool+'-native-contract',toolenv)
            results[tool]={'status':'passed','executed_this_attempt':True,'python':str(python),
                          'owned_runtime':str(prefix),'full_community_fit':False}
        except Exception as error:
            results[tool]={'status':'failed','error':repr(error),'dependent_stages_skipped':True}
            write_json(attempt/(tool+'-failure.json'),results[tool]);print('TOOL_CONTRACT_FAILURE='+json.dumps(results[tool]),flush=True)
        write_json(attempt/(tool+'-status.json'),results[tool])
    write_json(attempt/'native-contract-status.json',results)
    failed=[t for t in ['scgbinner','comebin'] if results[t]['status']!='passed']
    return {'status':'failed' if failed else 'passed','native_linux':not bool(local),'tools':results,'failed_tools':failed,
        'only_remaining_contracts':True,'owned_runtime_prefixes':prefixes,'reused_attempt':str(previous),
        'scope':'two failed tiny native contracts only; preserved v10 passed tools/stages/source assets; no full fits or E009 scores',
        'scientific_execution_admitted':False}
