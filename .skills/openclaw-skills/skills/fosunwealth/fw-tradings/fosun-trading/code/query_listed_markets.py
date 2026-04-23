#!/usr/bin/env python3
"""根据股票代码判断其是否在港股、美股、A股上市。

数据直接内嵌自:
  - t_ah_connect.csv
  - t_hk_adr_connect.csv

支持输入示例:
  00700
  hk00700
  600519
  sh600519
  AAPL
  usAAPL
  00700.HK
  600519.SH
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from collections import defaultdict


T_AH_CONNECT_CSV = """h_symbol,h_raw_symbol,a_symbol
hk00038,00038,sh601038
hk00107,00107,sh601107
hk00168,00168,sh600600
hk00177,00177,sh600377
hk00187,00187,sh600860
hk00300,00300,sz000333
hk00317,00317,sh600685
hk00323,00323,sh600808
hk00338,00338,sh600688
hk00347,00347,sz000898
hk00358,00358,sh600362
hk00386,00386,sh600028
hk00390,00390,sh601390
hk00470,00470,sz300450
hk00501,00501,sh603501
hk00525,00525,sh601333
hk00548,00548,sh600548
hk00553,00553,sh600775
hk00564,00564,sh601717
hk00568,00568,sz002490
hk00588,00588,sh601588
hk00598,00598,sh601598
hk00638,00638,sz300638
hk00670,00670,sh600115
hk00699,00699,sh600699
hk00719,00719,sz000756
hk00728,00728,sh601728
hk00753,00753,sh601111
hk00763,00763,sz000063
hk00811,00811,sh601811
hk00857,00857,sh601857
hk00874,00874,sh600332
hk00883,00883,sh600938
hk00895,00895,sz002672
hk00902,00902,sh600011
hk00914,00914,sh600585
hk00916,00916,sz001289
hk00921,00921,sz000921
hk00939,00939,sh601939
hk00941,00941,sh600941
hk00956,00956,sh600956
hk00981,00981,sh688981
hk00991,00991,sh601991
hk00995,00995,sh600012
hk00998,00998,sh601998
hk01033,01033,sh600871
hk01053,01053,sh601005
hk01055,01055,sh600029
hk01057,01057,sz002703
hk01065,01065,sh600874
hk01071,01071,sh600027
hk01072,01072,sh600875
hk01088,01088,sh601088
hk01108,01108,sh600876
hk01138,01138,sh600026
hk01157,01157,sz000157
hk01171,01171,sh600188
hk01186,01186,sh601186
hk01211,01211,sz002594
hk01276,01276,sh600276
hk01288,01288,sh601288
hk01304,01304,sh688279
hk01330,01330,sh601330
hk01336,01336,sh601336
hk01339,01339,sh601319
hk01347,01347,sh688347
hk01349,01349,sh688505
hk01375,01375,sh601375
hk01385,01385,sh688385
hk01398,01398,sh601398
hk01456,01456,sh601456
hk01513,01513,sz000513
hk01528,01528,sh601828
hk01618,01618,sh601618
hk01635,01635,sh600635
hk01658,01658,sh601658
hk01766,01766,sh601766
hk01772,01772,sz002460
hk01776,01776,sz000776
hk01787,01787,sh600547
hk01800,01800,sh601800
hk01816,01816,sz003816
hk01858,01858,sh688236
hk01877,01877,sh688180
hk01880,01880,sh601888
hk01898,01898,sh601898
hk01919,01919,sh601919
hk01963,01963,sh601963
hk01988,01988,sh600016
hk02009,02009,sh601992
hk02016,02016,sh601916
hk02039,02039,sz000039
hk02050,02050,sz002050
hk02068,02068,sh601068
hk02196,02196,sh600196
hk02202,02202,sz000002
hk02208,02208,sz002202
hk02218,02218,sh605198
hk02238,02238,sh601238
hk02315,02315,sh688796
hk02318,02318,sh601318
hk02333,02333,sh601633
hk02338,02338,sz000338
hk02359,02359,sh603259
hk02402,02402,sh688339
hk02465,02465,sh603906
hk02579,02579,sz300919
hk02600,02600,sh601600
hk02601,02601,sh601601
hk02603,02603,sz002803
hk02607,02607,sh601607
hk02611,02611,sh601211
hk02628,02628,sh601628
hk02631,02631,sh688234
hk02648,02648,sh603345
hk02676,02676,sh688052
hk02691,02691,sh603093
hk02692,02692,sz003021
hk02714,02714,sz002714
hk02715,02715,sz002747
hk02727,02727,sh601727
hk02768,02768,sz002768
hk02865,02865,sz002865
hk02866,02866,sh601866
hk02880,02880,sh601880
hk02883,02883,sh601808
hk02899,02899,sh601899
hk03200,03200,sz301200
hk03268,03268,sz002881
hk03288,03288,sh603288
hk03328,03328,sh601328
hk03347,03347,sz300347
hk03369,03369,sh601326
hk03606,03606,sh600660
hk03618,03618,sh601077
hk03678,03678,sz001236
hk03750,03750,sz300750
hk03759,03759,sz300759
hk03866,03866,sz002948
hk03898,03898,sh688187
hk03908,03908,sh601995
hk03958,03958,sh600958
hk03968,03968,sh600036
hk03969,03969,sh688009
hk03986,03986,sh603986
hk03988,03988,sh601988
hk03993,03993,sh603993
hk03996,03996,sh601868
hk06030,06030,sh600030
hk06031,06031,sh600031
hk06066,06066,sh601066
hk06099,06099,sh600999
hk06127,06127,sh603127
hk06160,06160,sh688235
hk06166,06166,sh603083
hk06178,06178,sh601788
hk06185,06185,sh688185
hk06196,06196,sz002936
hk06198,06198,sh601298
hk06613,06613,sz300433
hk06655,06655,sh600801
hk06680,06680,sz300748
hk06690,06690,sh600690
hk06693,06693,sh600988
hk06806,06806,sz000166
hk06809,06809,sh688008
hk06818,06818,sh601818
hk06821,06821,sz002821
hk06826,06826,sh688366
hk06865,06865,sh601865
hk06869,06869,sh601869
hk06881,06881,sh601881
hk06886,06886,sh601688
hk06936,06936,sz002352
hk09611,09611,sh603341
hk09696,09696,sz002466
hk09927,09927,sh601127
hk09969,09969,sh688428
hk09980,09980,sh605499
hk09981,09981,sz002130
hk09989,09989,sz002399
hk09995,09995,sh688331
"""


T_HK_ADR_CONNECT_CSV = """h_code,us_code
hk00001,usCKHUY
hk00002,usCLPHY
hk00003,usHOKCY
hk00004,usWARFY
hk00005,usHSBC
hk00006,usHGKGY
hk00008,usPCCWY
hk00010,usHNLGY
hk00012,usHLDCY
hk00013,usHCM
hk00014,usHYSNY
hk00016,usSUHJY
hk00017,usNDVLY
hk00019,usSWRAY
hk00019,usSWRBY
hk00023,usBKEAY
hk00027,usGXYYY
hk00038,usFIRRY
hk00045,usHKSHY
hk00053,usGULRY
hk00066,usMTCPY
hk00069,usSHALY
hk00083,usSNLAY
hk00086,usSHGKY
hk00087,usSWRAY
hk00087,usSWRBY
hk00097,usHDVTY
hk00101,usHLPPY
hk00127,usCESTY
hk00135,usKLYCY
hk00142,usFPAFY
hk00144,usCMHHY
hk00148,usKBDCY
hk00151,usWWNTY
hk00168,usTSGTY
hk00175,usGELHY
hk00177,usJEXYY
hk00178,usSAXJY
hk00179,usJEHLY
hk00200,usMDEVY
hk00210,usDPNEY
hk00215,usHUTCY
hk00220,usUPCHY
hk00241,usALBBY
hk00257,usCHFFY
hk00267,usCTPCY
hk00268,usKGDEY
hk00270,usGGDVY
hk00272,usSOLLY
hk00276,usMOAEY
hk00285,usBYDIY
hk00288,usWHGLY
hk00291,usCRHKY
hk00293,usCPCAY
hk00297,usSNFRY
hk00303,usVTKLY
hk00316,usOROVY
hk00321,usTXWHY
hk00322,usTYCMY
hk00330,usESPGY
hk00336,usHUIHY
hk00363,usSGHIY
hk00371,usBJWTY
hk00373,usALEDY
hk00384,usCGHLY
hk00388,usHKXCY
hk00425,usMNTHY
hk00440,usDSFGY
hk00489,usDNFGY
hk00506,usCHFHY
hk00511,usTVBCY
hk00522,usASMVY
hk00548,usSHZNY
hk00551,usYUEIY
hk00552,usCUCSY
hk00568,usSHANY
hk00581,usCUGCY
hk00590,usLKFKY
hk00656,usFOSUY
hk00658,usCHSTY
hk00659,usNWSGY
hk00669,usTTNDY
hk00670,usCHNEY
hk00683,usKRYPY
hk00688,usCAOVY
hk00694,usBJCHY
hk00696,usTSYHY
hk00700,usTCEHY
hk00737,usSIHBY
hk00751,usSWDHY
hk00753,usAIRYY
hk00788,usCTOWY
hk00800,usWRD
hk00809,usGBCMY
hk00813,usSHMAY
hk00817,usFRSHY
hk00825,usNWRLY
hk00829,usSHGXY
hk00836,usCRPJY
hk00861,usDCHIY
hk00868,usXYIGY
hk00880,usSJMHY
hk00881,usZSHGY
hk00914,usAHCHY
hk00916,usCLPXY
hk00934,usSPKOY
hk00939,usCICHY
hk00960,usLGFRY
hk00966,usCTIHY
hk00968,usXISHY
hk00992,usLNVGY
hk00998,usCHCJY
hk01024,usKSHTY
hk01038,usCKISY
hk01044,usHEGIY
hk01066,usSHWGY
hk01071,usHPIFY
hk01088,usCSUAY
hk01093,usCSPCY
hk01097,usICABY
hk01099,usSHTDY
hk01109,usCRBJY
hk01113,usCNGKY
hk01128,usWYNMY
hk01137,usHKTVY
hk01157,usZLIOY
hk01171,usYZCAY
hk01177,usSBHMY
hk01179,usHTHT
hk01193,usCGASY
hk01199,usCSPKY
hk01205,usCTJHY
hk01211,usBYDDY
hk01251,usSEGYY
hk01288,usACGBY
hk01299,usAAGIY
hk01308,usSITIY
hk01313,usCARCY
hk01339,usPINXY
hk01368,usXTEPY
hk01378,usCHHQY
hk01385,usSFDMY
hk01393,usHIIDY
hk01398,usIDCBY
hk01618,usMLLUY
hk01658,usPSTVY
hk01698,usTME
hk01725,usUSPCY
hk01766,usCRCCY
hk01772,usGNENY
hk01810,usXIACY
hk01818,usZHAOY
hk01836,usSLNLY
hk01876,usBDWBY
hk01888,usKGBLY
hk01898,usCCOZY
hk01910,usSMSEY
hk01913,usPRDSY
hk01919,usCICOY
hk01928,usSCHYY
hk01929,usCJEWY
hk01988,usCMAKY
hk01997,usWHREY
hk01999,usMAWHY
hk02009,usBBMPY
hk02015,usLI
hk02018,usAACAY
hk02020,usANPDY
hk02026,usPONY
hk02038,usFXCNY
hk02057,usZTO
hk02076,usBZ
hk02202,usCHVKY
hk02238,usGNZUY
hk02269,usWXXWY
hk02313,usSHZHY
hk02314,usLMPMY
hk02318,usPNGAY
hk02319,usCIADY
hk02328,usPPCCY
hk02331,usLNNGY
hk02333,usGWLLY
hk02343,usPCFBY
hk02359,usWUXAY
hk02378,usPUK
hk02382,usSOTGY
hk02388,usBHKLY
hk02390,usZH
hk02391,usTUYA
hk02423,usBEKE
hk02518,usATHM
hk02525,usHSAI
hk02607,usSHPMY
hk02688,usXNGSY
hk02689,usNDGPY
hk02727,usSIELY
hk02777,usGZUHY
hk02866,usCITAY
hk02877,usCSWYY
hk02888,usSCBFY
hk02899,usZIJMY
hk03303,usJUTOY
hk03306,usJNBBY
hk03323,usCBUMY
hk03328,usBCMXY
hk03337,usATONY
hk03339,usLKHLY
hk03368,usPKSGY
hk03377,usSIOLY
hk03382,usTJIPY
hk03383,usAGPYY
hk03606,usFYGGY
hk03618,usCRCBY
hk03660,usQFIN
hk03690,usMPNGY
hk03750,usCYATY
hk03808,usSHKLY
hk03818,usCDGXY
hk03888,usKGFTY
hk03896,usKC
hk03898,usZHUZY
hk03918,usNGCRY
hk03968,usCIHKY
hk03969,usCRYCY
hk03983,usCBLUY
hk03988,usBACHY
hk03993,usCMCLY
hk03998,usBSDGY
hk06030,usCIIHY
hk06060,usZZHGY
hk06128,usGRFXY
hk06160,usONC
hk06186,usCFEIY
hk06618,usJDHIY
hk06623,usLU
hk06686,usNOAH
hk06690,usHSHCY
hk06808,usSURRY
hk06855,usAAPG
hk06881,usCGXYY
hk09618,usJD
hk09626,usBILI
hk09658,usHDL
hk09688,usZLAB
hk09698,usGDS
hk09866,usNIO
hk09868,usXPEV
hk09888,usBIDU
hk09896,usMNSO
hk09898,usWB
hk09901,usEDU
hk09961,usTCOM
hk09988,usBABA
hk09991,usBZUN
hk09992,usPMRTY
hk09999,usNTES
"""


def _read_csv_rows(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(text.strip())))


AH_CONNECT_ROWS = _read_csv_rows(T_AH_CONNECT_CSV)
HK_ADR_CONNECT_ROWS = _read_csv_rows(T_HK_ADR_CONNECT_CSV)

HK_TO_A: dict[str, str] = {}
A_TO_HK: dict[str, str] = {}
HK_TO_US: dict[str, set[str]] = defaultdict(set)
US_TO_HK: dict[str, str] = {}

for row in AH_CONNECT_ROWS:
    hk_code = row["h_symbol"].strip().lower()
    a_code = row["a_symbol"].strip().lower()
    HK_TO_A[hk_code] = a_code
    A_TO_HK[a_code] = hk_code

for row in HK_ADR_CONNECT_ROWS:
    hk_code = row["h_code"].strip().lower()
    us_code = "us" + row["us_code"].strip()[2:].upper()
    HK_TO_US[hk_code].add(us_code)
    US_TO_HK[us_code] = hk_code


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def infer_a_market(raw_code: str) -> str:
    """根据 6 位纯数字代码推断沪深市场。"""
    if len(raw_code) != 6 or not raw_code.isdigit():
        raise ValueError(f"无法识别的 A 股代码: {raw_code}")
    if raw_code.startswith(("5", "6", "9")):
        return "sh" + raw_code
    return "sz" + raw_code


def normalize_code(code: str) -> str:
    """把用户输入统一转换成 hk/us/sh/sz 前缀格式。"""
    value = code.strip()
    if not value:
        raise ValueError("股票代码不能为空")

    if "." in value:
        left, right = value.rsplit(".", 1)
        market = right.lower()
        if market == "hk" and left.isdigit():
            return "hk" + left.zfill(5)
        if market in {"sh", "ss"} and left.isdigit():
            return "sh" + left.zfill(6)
        if market == "sz" and left.isdigit():
            return "sz" + left.zfill(6)
        if market == "us":
            return "us" + left.upper()

    compact = value.replace("-", "").replace("_", "")
    lower = compact.lower()

    if lower.startswith("hk") and lower[2:].isdigit():
        return "hk" + lower[2:].zfill(5)
    if lower.startswith(("sh", "sz")) and lower[2:].isdigit():
        return lower[:2] + lower[2:].zfill(6)
    if lower.startswith("us"):
        return "us" + compact[2:].upper()

    if compact.isdigit():
        if len(compact) <= 5:
            return "hk" + compact.zfill(5)
        if len(compact) == 6:
            return infer_a_market(compact)
        raise ValueError(f"无法识别的纯数字代码: {code}")

    return "us" + compact.upper()


def query_listed_markets(code: str) -> dict[str, object]:
    """查询股票在哪些市场上市。"""
    normalized = normalize_code(code)

    if normalized.startswith("hk"):
        hk_code = normalized
    elif normalized.startswith(("sh", "sz")):
        hk_code = A_TO_HK.get(normalized)
    else:
        hk_code = US_TO_HK.get(normalized)

    if not hk_code:
        return {
            "input_code": code,
            "normalized_code": normalized,
            "found": False,
            "message": "未在内置多地上市映射表中找到该代码",
        }

    a_code = HK_TO_A.get(hk_code)
    us_codes = sorted(HK_TO_US.get(hk_code, set()))
    listed_markets = [
        market
        for market, enabled in (
            ("hk", True),
            ("a", bool(a_code)),
            ("us", bool(us_codes)),
        )
        if enabled
    ]
    listed_market_names = [
        market_name
        for market_name, enabled in (
            ("港股", True),
            ("A股", bool(a_code)),
            ("美股", bool(us_codes)),
        )
        if enabled
    ]

    return {
        "input_code": code,
        "normalized_code": normalized,
        "found": True,
        "is_listed_in_hk": True,
        "is_listed_in_a": bool(a_code),
        "is_listed_in_us": bool(us_codes),
        "listed_markets": listed_markets,
        "listed_market_names": listed_market_names,
        "related_codes": {
            "hk": hk_code,
            "a": a_code,
            "us": us_codes,
        },
    }


def format_result(result: dict[str, object]) -> str:
    """格式化为易读文本输出。"""
    if not result["found"]:
        return "\n".join(
            [
                f"输入代码: {result['input_code']}",
                f"标准化后: {result['normalized_code']}",
                f"结果: {result['message']}",
            ]
        )

    related_codes = result["related_codes"]
    us_codes = related_codes["us"] or []

    return "\n".join(
        [
            f"输入代码: {result['input_code']}",
            f"标准化后: {result['normalized_code']}",
            f"是否港股上市: {'是' if result['is_listed_in_hk'] else '否'}",
            f"是否A股上市: {'是' if result['is_listed_in_a'] else '否'}",
            f"是否美股上市: {'是' if result['is_listed_in_us'] else '否'}",
            f"上市市场: {', '.join(result['listed_market_names'])}",
            f"港股代码: {related_codes['hk']}",
            f"A股代码: {related_codes['a'] or '-'}",
            f"美股代码: {', '.join(us_codes) if us_codes else '-'}",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="查询股票是否在港股、美股、A股上市")
    parser.add_argument("code", help="股票代码，如 00700 / hk00700 / 600519 / BABA")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = query_listed_markets(args.code)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_result(result))


if __name__ == "__main__":
    main()
