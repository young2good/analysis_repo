import altair as alt
import pandas as pd


def sido_bar_chart(df: pd.DataFrame) -> alt.Chart:
    sido_counts = df["sido"].value_counts().reset_index()
    sido_counts.columns = ["sido", "count"]

    return alt.Chart(sido_counts).mark_bar(color="hotpink").encode(
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

    return alt.Chart(sigungu_counts).mark_bar(color="hotpink").encode(
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
        color=alt.condition(selection, alt.value("hotpink"), alt.value("lightgray")),
        tooltip=["sido:N", "count():Q"]
    ).properties(
        title="시도별 게시글 수",
        width=400,
        height=400
    ).add_params(selection)

    sigungu_chart = base.mark_bar(color="hotpink").encode(
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


AXIS_CONFIG = dict(domain=False, ticks=False, grid=False)
