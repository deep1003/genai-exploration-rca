# Cell 9-(1): Core and Periphery estimation for US, CN, KR using a two-block SBM (MLE, greedy)
#  ── 목적: 2블록 SBM(Core/Periphery)을 기간별 그래프에 적합하고 국가별 요약 지표 산출
#  ── 입력: G_periods(기간-그래프), df_network_llm['inventor'], ['inventor_nat'], EU_CODES
#  ── 출력: df_summary(기간 인덱스, 국가별 노드·비율·Core 비중 요약)

# ── 주피터 노트북에서 그래프를 인라인 출력
  

import pandas as pd    # ── 데이터프레임 연산
import networkx as nx  # ── 네트워크(그래프) 자료구조 및 변환
import numpy as np     # ── 수치 연산(고속 배열, 선형대수)

print("Subtitle: Core and Periphery estimation for US, CN, KR using a two-block SBM (MLE, greedy)")  # ── 영어 소제목 출력

# ── 분석 대상 국가(요약 표에 별도 컬럼 생성)
focus_countries = ["US", "CN", "KR"]

def _sbm_fit_core_periphery(G, max_iters=50, eps=1e-9, seed=42):
    """
    Fit a 2-block Bernoulli SBM (Core/Periphery) by greedy maximum likelihood.
    Returns: dict {node: 1 if Core, 0 if Periphery}
    """
    rng = np.random.default_rng(seed)   # ── 재현 가능한 난수 시드
    nodes = list(G.nodes())             # ── 노드 리스트 추출
    n = len(nodes)                      # ── 노드 수
    if n == 0:
        return {}                       # ── 빈 그래프 처리

    # ── 인접행렬로 변환(가중치가 있으면 이진화)
    A = nx.to_numpy_array(G, nodelist=nodes)
    if np.any(A != A.astype(bool)):
        A = (A > 0).astype(int)        # ── 0/1 이진화
    else:
        A = A.astype(int)

    # ── 스펙트럴 초기화(최대 고유값의 고유벡터 절댓값을 정규화하여 중간값 기준 이진 분류)
    vals, vecs = np.linalg.eigh(A)      # ── 대칭행렬 고유분해
    v = np.abs(vecs[:, np.argmax(vals)])                 # ── 최대 고유값 대응 고유벡터의 절댓값
    v_norm = (v - v.min()) / (v.max() - v.min() + eps)   # ── 0~1 스케일 정규화
    thr = np.median(v_norm)             # ── 임계값: 중앙값
    z = (v_norm >= thr).astype(int)     # ── 초기 라벨(1=Core, 0=Periphery)

    # ── 두 집단이 모두 비지 않도록 보정
    if z.sum() == 0:
        z[rng.integers(0, n)] = 1
    if z.sum() == n:
        z[rng.integers(0, n)] = 0

    # ── 탐욕적 최대우도 갱신 반복
    for _ in range(max_iters):
        changed = 0

        # ── 현재 라벨에서 집단 인덱스와 크기 계산
        idxC = np.where(z == 1)[0]
        idxP = np.where(z == 0)[0]
        nC, nP = len(idxC), len(idxP)

        # ── 가능한 간선쌍 개수(0 나눗셈 방지)
        Ncc = max(nC * (nC - 1) // 2, 1)
        Npp = max(nP * (nP - 1) // 2, 1)
        Ncp = max(nC * nP, 1)

        # ── 블록별 실제 간선 수 집계
        m_cc = int(A[np.ix_(idxC, idxC)].sum() // 2) if nC >= 2 else 0
        m_pp = int(A[np.ix_(idxP, idxP)].sum() // 2) if nP >= 2 else 0
        m_cp = int(A[np.ix_(idxC, idxP)].sum())

        # ── 블록 확률의 MLE(수치 안정성 위해 클리핑)
        p_cc = np.clip(m_cc / Ncc, eps, 1 - eps)
        p_pp = np.clip(m_pp / Npp, eps, 1 - eps)
        p_cp = np.clip(m_cp / Ncp, eps, 1 - eps)

        # ── 각 노드의 C/P 연결 정도수(벡터화 합계)
        k_to_C = A[:, idxC].sum(axis=1)
        k_to_P = A[:, idxP].sum(axis=1)

        # ── 각 노드에 대해 Core로 둘 때와 Periphery로 둘 때의 로그우도 비교
        for i in range(n):
            # ── 자기 자신 제외한 유효 집단 크기
            nC_i = nC - 1 if z[i] == 1 else nC
            nP_i = nP - 1 if z[i] == 0 else nP

            # ── i의 C, P로 향한 연결 수(대각 원소 제외)
            k_iC = k_to_C[i] - (A[i, i] if z[i] == 1 else 0)
            k_iP = k_to_P[i] - (A[i, i] if z[i] == 0 else 0)

            # ── i를 Core로 둘 때의 로그우도
            LL_core = (
                k_iC * np.log(p_cc) + (max(nC_i, 0) - k_iC) * np.log(1 - p_cc) +
                k_iP * np.log(p_cp) + (max(nP_i, 0) - k_iP) * np.log(1 - p_cp)
            )
            # ── i를 Periphery로 둘 때의 로그우도
            LL_peri = (
                k_iC * np.log(p_cp) + (max(nC_i, 0) - k_iC) * np.log(1 - p_cp) +
                k_iP * np.log(p_pp) + (max(nP_i, 0) - k_iP) * np.log(1 - p_pp)
            )

            # ── 더 큰 로그우도를 주는 라벨로 업데이트
            new_label = 1 if LL_core > LL_peri else 0
            if new_label != z[i]:
                z[i] = new_label
                changed += 1

        # ── 더 이상 변경이 없으면 수렴으로 종료
        if changed == 0:
            break

    # ── 노드:라벨 매핑 반환(1=Core, 0=Periphery)
    return {nodes[i]: int(z[i]) for i in range(n)}

# ----------------------------
# Compute metrics by period
# ----------------------------
metrics = []  # ── 결과 누적 리스트
for period, Gp in G_periods.items():
    nodes = list(Gp.nodes())               # ── 해당 기간의 노드 목록
    total_nodes = len(nodes)               # ── 노드 총수

    # ── 2블록 SBM 적합(Core=1, Periphery=0)
    z_map = _sbm_fit_core_periphery(Gp)
    total_cores = sum(z_map[n] for n in nodes)   # ── Core 총수

    # ── 발명가 → 국적 매핑 생성(첫 일치값 사용)
    nationality = {
        n: df_network_llm.loc[df_network_llm["inventor"] == n, "inventor_nat"].iloc[0]
        for n in nodes
    }

    # ── 국적을 분석 그룹으로 사상(EU, GB, 기타 포함)
    group = {
        n: (
            "CN" if nationality[n] == "CN" else
            "US" if nationality[n] == "US" else
            "KR" if nationality[n] == "KR" else
            "EU" if nationality[n] in EU_CODES else
            "GB" if nationality[n] == "GB" else
            "Others"
        )
        for n in nodes
    }

    # ── 한 기간에 대한 요약 행 구성
    row = {
        "Period":      period,        # ── 기간 키
        "Total Nodes": total_nodes,   # ── 전체 노드 수
        "Core Size":   total_cores    # ── Core 노드 수
    }

    # ── 주요 3개국 통계(노드 수, 전체 대비 비율, Core 수, Core 내 비율)
    for c in focus_countries:
        country_nodes      = [n for n in nodes if group[n] == c]      # ── 해당국 노드 목록
        country_total      = len(country_nodes)                        # ── 해당국 노드 수
        country_core_count = sum(z_map[n] for n in country_nodes)      # ── 해당국 Core 수

        row[f"{c} Nodes"]           = country_total                                   # ── 노드 수
        row[f"{c} Node Ratio (%)"]  = country_total / total_nodes * 100 if total_nodes else 0  # ── 전체 대비 비율
        row[f"{c} Core Nodes"]      = country_core_count                               # ── Core 수
        row[f"{c} Core Ratio (%)"]  = country_core_count / total_cores * 100 if total_cores else 0  # ── Core 내 비율

    metrics.append(row)  # ── 결과 추가

# ── 기간 인덱스의 요약 테이블 생성
df_summary = pd.DataFrame(metrics).set_index("Period")  # ── 최종 요약 데이터프레임
df_summary  # ── 영어 컬럼명으로 출력
