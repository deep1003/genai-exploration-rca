# Cell 7-(1a2): t-SNE with prior PCA to 50D, visualising GenAI vs Others in 2D
#  ── 목적: X_all → PCA(최대 50차원) → t-SNE(2D) 투영, GenAI vs Others 산점도
#  ── 입력: X_all (NumPy 배열), df_pred["genai_pred"] (이진 라벨)
#  ── 출력: 산점도(plt.show), 보조 테이블(vis_df), 좌표(X_tsne)

from sklearn.manifold import TSNE          # ── t-SNE 차원 축소
from sklearn.decomposition import PCA      # ── PCA 사전 축소
import numpy as np, pandas as pd, matplotlib.pyplot as plt, seaborn as sns, time, inspect
from tqdm import tqdm

print("Subtitle: t-SNE with prior PCA to 50D, visualising GenAI vs Others in 2D")  # ── 영어 소제목 출력

# -----------------------------
# 0) 입력 검증 및 길이 정렬
# -----------------------------
X = np.asarray(X_all)                         # ── X_all을 NumPy 배열로 강제 변환
n = X.shape[0]                                # ── 표본 수 저장
labels = df_pred["genai_pred"].astype(str).values  # ── 이진 라벨(문자열) 추출
m = len(labels)

if n != m:
    # ── 길이 불일치 시 공통 최소 길이로 절단하여 인덱스 정합성 확보
    k = min(n, m)
    X = X[:k]
    labels = labels[:k]
    print(f"[warn] Length mismatch: X_all={n}, labels={m} → truncated to {k}")

# -----------------------------
# 1) PCA 사전 축소(최대 50차원)
# -----------------------------
# ── t-SNE 안정성·속도 개선을 위해 고차원을 50차원 이하로 축소
pca_k = 50 if X.shape[1] > 50 else X.shape[1]      # ── 원 차원이 50 이하이면 그대로 사용
t0 = time.time()
X_pca = PCA(n_components=pca_k, svd_solver="randomized", random_state=42).fit_transform(X)
print(f"[PCA] reduced to {pca_k} dims in {time.time() - t0:.1f}s")

# -----------------------------
# 2) perplexity 자동 조정
# -----------------------------
# ── t-SNE 제약: n_samples > 3 * perplexity 조건을 만족하도록 상한 설정
base_perp = 30
max_valid_perp = max(5, (len(X_pca) - 1) // 3)
perp = min(base_perp, max_valid_perp)

# -----------------------------
# 3) TSNE 인자 호환성 처리
# -----------------------------
# ── sklearn 버전에 따라 n_iter 또는 max_iter 사용 여부를 런타임 점검
tsne_sig = inspect.signature(TSNE.__init__).parameters
tsne_common = dict(
    n_components=2,          # ── 최종 2차원 좌표 계산
    perplexity=perp,         # ── 위에서 계산한 perplexity 적용
    init="random",           # ── 랜덤 초기화로 지역 극값 민감도 완화
    random_state=42,         # ── 재현성 보장
)
if "n_iter" in tsne_sig:
    tsne_kwargs = dict(tsne_common, n_iter=1000)        # ── 구버전 호환
elif "max_iter" in tsne_sig:
    tsne_kwargs = dict(tsne_common, max_iter=1000)      # ── 신버전 호환
else:
    tsne_kwargs = tsne_common                           # ── 기본값 사용

# -----------------------------
# 4) 파이프라인 실행
# -----------------------------
steps = ["Compute t-SNE", "Prepare DataFrame", "Compute Summary", "Plot Scatter"]
X_tsne = None     # ── t-SNE 결과 좌표 초기화
vis_df = None     # ── 시각화용 데이터프레임 초기화

for step in tqdm(steps, desc="t-SNE Pipeline", unit="step"):
    if step == "Compute t-SNE":
        # ── PCA 결과(X_pca)를 입력으로 t-SNE 학습 및 2D 좌표 획득
        print(f"[t-SNE] fitting GenAI view… (perplexity={perp})")
        t1 = time.time()
        tsne = TSNE(**tsne_kwargs)
        X_tsne = tsne.fit_transform(X_pca)
        print(f"[t-SNE] done in {time.time() - t1:.1f}s")

    elif step == "Prepare DataFrame":
        # ── t-SNE 좌표와 이진 라벨을 결합하여 시각화 테이블 생성
        vis_df = pd.DataFrame({
            "tSNE1": X_tsne[:, 0],
            "tSNE2": X_tsne[:, 1],
            "GenAI": pd.Series(labels).apply(lambda x: "GenAI" if x == "GenAI" else "Others")
        })

    elif step == "Compute Summary":
        # ── 클래스별 개수와 비율을 계산하여 범례에 반영할 문자열 구성
        counts = vis_df["GenAI"].value_counts()
        total  = len(vis_df)
        summary_labels = {cls: f"{cls} ({counts[cls]}/{total} = {counts[cls]/total:.1%})"
                          for cls in counts.index}

    elif step == "Plot Scatter":
        # ── 산점도 시각화(플롯 내 텍스트와 범례는 영문 유지)
        plt.figure(figsize=(10, 6))
        ax = sns.scatterplot(
            data=vis_df,
            x="tSNE1", y="tSNE2",
            hue="GenAI",
            palette={"Others": "lightgray", "GenAI": "crimson"},
            alpha=0.6,
            s=40,
            edgecolor="white"
        )
        plt.title("t-SNE: GenAI vs Others")     # ── 제목(영문)
        plt.xlabel("t-SNE Component 1")         # ── x축 레이블(영문)
        plt.ylabel("t-SNE Component 2")         # ── y축 레이블(영문)

        # ── 범례 라벨을 개수·비율 정보로 대체
        handles, labels_ = ax.get_legend_handles_labels()
        new_labels = [summary_labels.get(lab, lab) for lab in labels_]
        ax.legend(handles=handles, labels=new_labels, title="Classification",
                  bbox_to_anchor=(1.05, 1), loc="upper left")

        plt.tight_layout()
        plt.show()
