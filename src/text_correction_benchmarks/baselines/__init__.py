import argparse
import sys
from typing import Any, Dict, Iterable, Optional

from text_correction_utils import text, unicode


class Baselines:
    # Sequence-level spelling error detection
    SEDS_DUMMY = "seds_dummy"
    SEDS_OOD = "seds_ood"
    SEDS_FROM_SEC = "seds_from_sec"

    # Word-level spelling error detection
    SEDW_DUMMY = "sedw_dummy"
    SEDW_OOD = "sedw_ood"
    SEDW_FROM_SEC = "sedw_from_sec"

    # Spelling error correction
    SEC_DUMMY = "sec_dummy"
    # not deep learning based
    SEC_CTD = "sec_ctd"
    SEC_JAMSPELL = "sec_jamspell"
    SEC_HUNSPELL = "sec_hunspell"
    SEC_ASPELL = "sec_aspell"
    SEC_NORVIG = "sec_norvig"
    # deep learning based
    SEC_NEUSPELL_BERT = "sec_neuspell_bert"

    # Whitespace correction
    WC_DUMMY = "wc_dummy"


class Baseline:
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed

    def run(self, sequences: Iterable[str], **kwargs: Dict[str, Any]) -> Iterable[str]:
        raise NotImplementedError

    @property
    def name(self) -> str:
        raise NotImplementedError


def get_baseline(baseline: str) -> Baseline:
    if baseline == Baselines.SEDS_DUMMY:
        from text_correction_benchmarks.baselines.seds import Dummy
        return Dummy()
    elif baseline == Baselines.SEDW_DUMMY:
        from text_correction_benchmarks.baselines.sedw import Dummy
        return Dummy()
    elif baseline == Baselines.SEC_DUMMY:
        from text_correction_benchmarks.baselines.sec import Dummy
        return Dummy()
    elif baseline == Baselines.WC_DUMMY:
        from text_correction_benchmarks.baselines.wc import Dummy
        return Dummy()
    else:
        raise ValueError(f"unknown baseline {baseline}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        "Text correction baselines",
        "Run a text correction baseline on corrupted text"
    )
    parser.add_argument(
        "baseline",
        choices=[
            baseline
            for key, baseline in vars(Baselines).items()
            if not key.startswith("_")
        ],
        help="Which baseline to run"
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        default=None,
        help="Run baseline on this file instead of stdin"
    )
    parser.add_argument(
        "-o",
        "--out",
        type=str,
        default=None,
        help="Path to output file"
    )
    parser.add_argument(
        "-n",
        "--normalization",
        type=str,
        help="Normalization to apply to the input text before running the baseline"
    )
    return parser.parse_args()


def prepare(
    sequences: Iterable[str],
    normalization: Optional[str] = None
) -> Iterable[str]:
    for s in sequences:
        s = text.clean(s)
        if normalization is not None:
            s = unicode.normalize(s, normalization)
        yield s


def run(args: argparse.Namespace):
    # prepare baseline and input
    baseline = get_baseline(args.baseline)
    if args.file is None:
        sequences = sys.stdin
    else:
        sequences = open(args.file, "r", encoding="utf8")

    if args.out is not None:
        of = open(args.out, "w", encoding="utf8")
    else:
        of = None

    # run the baseline
    for s in baseline.run(prepare(sequences, args.normalization)):
        if of is not None:
            of.write(f"{s}\n")
        else:
            print(s)

    # properly close the opened files
    if of is not None:
        of.close()
    if args.file is not None:
        sequences.close()


def main():
    run(parse_args())
