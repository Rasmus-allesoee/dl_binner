#!/usr/bin/env bash
# Owner-run Linux setup only. No data acquisition, binning, or training.
set -euo pipefail

tool=${1:?Usage: bash scripts/e001_linux_setup.sh mapping|amber|vamb|comebin|metabat WORK_ROOT}
root=${2:?Provide an absolute external work directory}
case "$root" in /*) ;; *) printf '%s\n' 'WORK_ROOT must be absolute' >&2; exit 2 ;; esac
[[ $(uname -s) == Linux && $(uname -m) == x86_64 ]] || { printf '%s\n' 'Linux x86_64 required' >&2; exit 2; }
command -v micromamba >/dev/null
command -v git >/dev/null
code=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
prefix="$root/envs/$tool"
[[ ! -e "$prefix" && ! -e "$root/locks/$tool" ]] || { printf '%s\n' 'Environment/lock directory already exists; inspect before retrying' >&2; exit 2; }
mkdir -p "$root/sources" "$root/locks/$tool"
exec > >(tee "$root/locks/$tool/setup.stdout") 2> >(tee "$root/locks/$tool/setup.stderr" >&2)
trap 'status=$?; printf "%s\n" "$status" > "$root/locks/$tool/setup.exit-code.txt"; printf "%s\n" "$SECONDS" > "$root/locks/$tool/setup.elapsed-seconds.txt"' EXIT
export MAMBA_ROOT_PREFIX="$root/micromamba" PIP_CACHE_DIR="$root/cache/pip"
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1

create_env() {
    micromamba create -y -p "$prefix" --strict-channel-priority -c conda-forge -c bioconda "$@"
}

clone_source() {
    git clone --no-checkout "$2" "$root/sources/$1"
    git -C "$root/sources/$1" checkout --detach "$3"
    [[ $(git -C "$root/sources/$1" rev-parse HEAD) == "$3" ]]
}

case "$tool" in
    mapping)
        create_env python=3.12.10 pip=25.1.1 numpy=2.2.6 biopython=1.85 pysam=0.23.3 strobealign=0.17.0 samtools=1.24
        ;;
    amber)
        clone_source AMBER_evaluation https://github.com/CAMI-challenge/AMBER.git f8b3a601043d13fc4227d5691c13561eb4490e50
        create_env python=3.12.10 pip=25.1.1
        micromamba run -p "$prefix" python -m pip install -r "$root/sources/AMBER_evaluation/requirements.txt" pysam==0.23.3
        ;;
    vamb)
        clone_source vamb https://github.com/RasmussenLab/vamb.git b146fb610921aef1da8aed5d739f1ce80d21b33a
        create_env python=3.12.10 pip=25.1.1
        micromamba run -p "$prefix" python -m pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu
        micromamba run -p "$prefix" python -m pip install "$root/sources/vamb" biopython==1.85 pysam==0.23.3
        ;;
    comebin)
        clone_source COMEBin https://github.com/ziyewang/COMEBin.git 1b476a41fac893294c70212a869573a732560ce5
        micromamba create -y -p "$prefix" -f "$root/sources/COMEBin/comebin_env.yaml" --strict-channel-priority
        micromamba run -p "$prefix" python -m pip install torch==2.13.0 --index-url https://download.pytorch.org/whl/cpu
        micromamba run -p "$prefix" python -m pip install pysam==0.23.3
        ;;
    metabat)
        clone_source metabat https://bitbucket.org/berkeleylab/metabat.git 8eb96023ef627d1955c05e3aca348c84b8757914
        create_env python=3.12.10 pip=25.1.1 numpy=2.2.6 biopython=1.85 pysam=0.23.3 cmake=3.31.6 make=4.4.1 c-compiler=1.9.0 cxx-compiler=1.9.0 boost-cpp=1.85.0 htslib=1.24 zlib=1.3.1
        micromamba run -p "$prefix" cmake -S "$root/sources/metabat" -B "$root/build/metabat" -DCMAKE_INSTALL_PREFIX="$prefix" -DCMAKE_PREFIX_PATH="$prefix" -DNO_TESTING=ON
        micromamba run -p "$prefix" cmake --build "$root/build/metabat" --parallel 2
        micromamba run -p "$prefix" cmake --install "$root/build/metabat"
        sha256sum "$prefix/bin/metabat2" "$prefix/bin/jgi_summarize_bam_contig_depths" > "$root/locks/$tool/binaries.sha256"
        ;;
    *) printf '%s\n' "Unknown tool: $tool" >&2; exit 2 ;;
esac

micromamba list -p "$prefix" --explicit > "$root/locks/$tool/conda-explicit.txt"
micromamba run -p "$prefix" python -m pip freeze --all > "$root/locks/$tool/pip-freeze.txt"
micromamba run -p "$prefix" python -m pip check > "$root/locks/$tool/pip-check.txt"
micromamba run -p "$prefix" python -c 'import platform,sys; print(sys.version); print(platform.platform())' > "$root/locks/$tool/platform.txt"
sha256sum "$code/scripts/e001_linux_setup.sh" > "$root/locks/$tool/setup-script.sha256"
printf '%s\n' 'Setup completed. Resolved locks still need inspection; native smoke and scientific runs are not complete.'
