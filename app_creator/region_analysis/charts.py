import altair as alt
import pandas as pd

C_PRIMARY   = "#63C1BB"  # teal (main)
C_SECONDARY = "#447B7E"  # dark teal
C_ACCENT    = "#F78535"  # orange
C_INACTIVE  = "#D9D9D9"  # light gray
C_GRAD_LOW  = "#E0F4F3"  # gradient light end

BOARD_PALETTE = ["#C8E6E2", "#9ED5D1", "#63C1BB", "#3A9295", "#105F68"]


def sido_bar_chart(df: pd.DataFrame) -> alt.Chart:
    sido_counts = df["sido"].value_counts().reset_index()
    sido_counts.columns = ["sido", "count"]

    return alt.Chart(sido_counts).mark_bar(color=C_PRIMARY).encode(
        x=alt.X("count:Q", title="게시글 수"),
        y=alt.Y("sido:N", sort="-x", title="시도"),
        tooltip=["sido", "count"]
    ).properties(
        title="시도별 게시글 수",
        width=600,
        height=400
    )


def sigungu_bar_chart(df: pd.DataFrame) -> alt.Chart:
    sigungu_counts = df["sigungu"].value_counts().reset_index()
    sigungu_counts.columns = ["sigungu", "count"]

    return alt.Chart(sigungu_counts).mark_bar(color=C_PRIMARY).encode(
        x=alt.X("count:Q", title="게시글 수"),
        y=alt.Y("sigungu:N", sort="-x", title="시군구"),
        tooltip=["sigungu", "count"]
    ).properties(
        title="시군구별 게시글 수",
        width=600,
        height=600
    )


def interactive_sido_sigungu_chart(df: pd.DataFrame) -> alt.HConcatChart:
    base_df = df.dropna(subset=["sido", "sigungu"])
    selection = alt.selection_point(fields=["sido"])
    base = alt.Chart(base_df)

    sido_chart = base.mark_bar().encode(
        x=alt.X("count():Q", title="게시글 수"),
        y=alt.Y("sido:N", sort="-x", title="시도"),
        color=alt.condition(selection, alt.value(C_PRIMARY), alt.value(C_INACTIVE)),
        tooltip=["sido:N", "count():Q"]
    ).properties(
        title="시도별 게시글 수",
        width=400,
        height=400
    ).add_params(selection)

    sigungu_chart = base.mark_bar(color=C_PRIMARY).encode(
        x=alt.X("count():Q", title="게시글 수"),
        y=alt.Y("sigungu:N", sort="-x", title="시군구"),
        tooltip=["sigungu:N", "count():Q"]
    ).transform_filter(
        selection
    ).properties(
        title="시군구별 게시글 수",
        width=400,
        height=400
    )

    return (sido_chart | sigungu_chart)


def board_pie_chart(df: pd.DataFrame, title: str = "게시판별 게시글 비중") -> alt.LayerChart:
    board_counts = df["board"].value_counts().reset_index()
    board_counts.columns = ["board", "count"]
    board_counts["pct"] = (board_counts["count"] / board_counts["count"].sum() * 100).round(1)
    board_counts["label"] = board_counts.apply(
        lambda r: r["board"].replace(" 주말축구", "") + "\n" + f"{r['count']:,}개 ({r['pct']:.1f}%)",
        axis=1
    )
    # theta 스택 순서를 데이터 순서(내림차순)에 고정
    board_counts["_order"] = range(len(board_counts))

    # 경기북부 슬라이스만 오렌지 하이라이트
    colors = [
        C_ACCENT if b == "경기북부 주말축구" else c
        for b, c in zip(list(board_counts["board"]), BOARD_PALETTE[:len(board_counts)])
    ]

    base = alt.Chart(board_counts).encode(
        theta=alt.Theta("count:Q", stack=True),
        order=alt.Order("_order:Q"),
        color=alt.Color(
            "board:N",
            legend=None,
            scale=alt.Scale(
                domain=list(board_counts["board"]),
                range=colors
            )
        ),
        tooltip=[
            alt.Tooltip("board:N", title="게시판"),
            alt.Tooltip("count:Q", title="게시글 수"),
            alt.Tooltip("pct:Q", title="비중(%)", format=".1f"),
        ]
    )

    arc = base.mark_arc(innerRadius=60, outerRadius=130)

    text = base.mark_text(radius=168, fontSize=11, lineBreak="\n").encode(
        text=alt.Text("label:N"),
        color=alt.value("#333"),
    )

    return (arc + text).properties(
        title=title,
        width=420,
        height=420,
    )


def interactive_zone_sigungu_chart(df: pd.DataFrame) -> alt.HConcatChart:
    base_df = df.dropna(subset=["zone", "sigungu"])
    selection = alt.selection_point(fields=["zone"])
    base = alt.Chart(base_df)

    zone_chart = base.mark_bar().encode(
        x=alt.X("count():Q", title="게시글 수"),
        y=alt.Y("zone:N", sort="-x", title="권역"),
        color=alt.condition(selection, alt.value(C_PRIMARY), alt.value(C_INACTIVE)),
        tooltip=["zone:N", "count():Q"]
    ).properties(
        title="권역별 게시글 수",
        width=400,
        height=450,
    ).add_params(selection)

    sigungu_chart = base.mark_bar(color=C_PRIMARY).encode(
        x=alt.X("count():Q", title="게시글 수"),
        y=alt.Y("sigungu:N", sort="-x", title="시군구"),
        tooltip=["sigungu:N", "count():Q"]
    ).transform_filter(
        selection
    ).properties(
        title="시군구별 게시글 수",
        width=400,
        height=450,
    )

    return (zone_chart | sigungu_chart)


def zone_bar_chart(df: pd.DataFrame) -> alt.Chart:
    zone_counts = (
        df.dropna(subset=["zone"])["zone"]
        .value_counts()
        .reset_index()
    )
    zone_counts.columns = ["zone", "count"]
    zone_counts["sido"] = zone_counts["zone"].str.split(" ").str[0]

    return alt.Chart(zone_counts).mark_bar().encode(
        x=alt.X("count:Q", title="게시글 수"),
        y=alt.Y("zone:N", sort="-x", title="권역"),
        color=alt.Color(
            "sido:N",
            title="시도",
            scale=alt.Scale(
                domain=["서울", "경기"],
                range=[C_PRIMARY, C_SECONDARY]
            )
        ),
        tooltip=[
            alt.Tooltip("zone:N", title="권역"),
            alt.Tooltip("count:Q", title="게시글 수"),
        ]
    ).properties(
        title="권역별 게시글 수",
        width=600,
        height=500,
    )


def sido_pie_chart(df: pd.DataFrame) -> alt.Chart:
    sido_counts = df["sido"].value_counts().reset_index()
    sido_counts.columns = ["sido", "count"]

    return alt.Chart(sido_counts).mark_arc().encode(
        theta=alt.Theta("count:Q"),
        color=alt.Color("sido:N", title="시도"),
        tooltip=["sido:N", "count:Q"]
    ).properties(
        title="시도별 게시글 비율",
        width=400,
        height=400
    )


AXIS_CONFIG = dict(domain=False, ticks=False, grid=False)
