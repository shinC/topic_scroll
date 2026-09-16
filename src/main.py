import asyncio
import sys
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table

from config import settings
from models.article import Article
from pipeline.exporter import ArticleExporter
from pipeline.google_sheets_exporter import GoogleSheetsExporter
from pipeline.processor import ArticleProcessor
from scrapers.registry import scraper_registry
from utils.http_client import get_http_client
from utils.logger import logger

app = typer.Typer(
    help="topic_scroll: 파이썬 3.14 기반 뉴스 수집 및 구글 스프레드시트 연동 엔진",
    add_completion=False,
)
console = Console()


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context):
    """스크래퍼 자동 등록 및 환경 구성을 초기화합니다."""
    scraper_registry.auto_discover()
    if ctx.invoked_subcommand is None:
        console.print("[bold blue]전체 뉴스/포털 수집 실행 (python src/main.py)...[/bold blue]\n")
        all_names = [s.name for s in scraper_registry.get_all_scrapers()]
        asyncio.run(_run_target_scrapers(all_names, settings.EXPORT_FORMAT, True))




@app.command("list")
def list_scrapers():
    """
    등록된 뉴스 사이트 스크래퍼 목록을 조회합니다.
    """
    scrapers = scraper_registry.get_all_scrapers()

    table = Table(title="[bold green]등록된 뉴스 스크래퍼 목록[/bold green]")
    table.add_column("스크래퍼 ID (Name)", style="cyan", no_wrap=True)
    table.add_column("언론사 / 사이트명", style="magenta")
    table.add_column("기본 URL", style="blue")

    for scraper in scrapers:
        table.add_row(scraper.name, scraper.site_name, scraper.base_url)

    console.print(table)
    console.print(
        f"\n총 [bold yellow]{len(scrapers)}[/bold yellow]개의 스크래퍼가 등록되어 있습니다."
    )


async def _run_target_scrapers(
    target_names: list[str], export_format: str, export_sheets: bool, save_file: bool = False
):
    """지정한 스크래퍼 목록 비동기 실행 및 내보내기 처리 내부 함수"""
    scrapers = [
        scraper_registry.get_scraper(name)
        for name in target_names
        if name in [s.name for s in scraper_registry.get_all_scrapers()]
    ]

    if not scrapers:
        console.print(
            f"[bold red]오류:[/bold red] 지정한 스크래퍼({target_names})를 찾을 수 없습니다."
        )
        return

    console.print(
        f"[bold blue]총 {len(scrapers)}개 스크래퍼 수집 시작...[/bold blue]"
    )

    async with get_http_client() as client:
        tasks = [scraper.run(client=client) for scraper in scrapers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    processor = ArticleProcessor()
    exporter = ArticleExporter()

    all_processed_articles: list[Article] = []

    for res in results:
        if isinstance(res, Exception):
            logger.error(f"스크래퍼 실행 오류: {str(res)}")
            continue

        if res.success and res.articles:
            res.articles = processor.process(res.articles)
            res.total_count = len(res.articles)
            all_processed_articles.extend(res.articles)

            if save_file:
                output_file = exporter.export_result(res, format_type=export_format)
                console.print(
                    f" - [{res.site_name}] {res.total_count}개 수집 완료 -> 로컬 저장: [cyan]{output_file}[/cyan]"
                )
            else:
                console.print(
                    f" - [{res.site_name}] {res.total_count}개 수집 처리 완료"
                )
        else:
            console.print(
                f" - [{res.site_name}] 수집 실패: {res.error_message or '기사를 찾을 수 없습니다.'}"
            )

    console.print(
        f"\n[bold green]수집 완료![/bold green] 총 [bold yellow]{len(all_processed_articles)}[/bold yellow]개 기사 수집됨."
    )

    # 구글 스프레드시트 내보내기
    if export_sheets:
        console.print(
            "\n[bold blue][Google Sheets] 구글 스프레드시트로 데이터를 내보내는 중... (덮어쓰기 모드)[/bold blue]"
        )
        sheets_exporter = GoogleSheetsExporter()
        success = sheets_exporter.export(all_processed_articles)
        if success:
            console.print(
                "[bold green][Google Sheets] 스프레드시트 덮어쓰기 저장 완료![/bold green]"
            )
        else:
            console.print(
                "[bold red][Google Sheets] 스프레드시트 저장 실패. 키 파일 및 권한을 확인해주세요.[/bold red]"
            )


@app.command("run-rss")
def run_rss(
    format: str = typer.Option(
        settings.EXPORT_FORMAT, "--format", "-f", help="파일 저장 포맷 (json, jsonl, csv)"
    ),
    sheets: bool = typer.Option(
        True, "--sheets/--no-sheets", help="구글 스프레드시트 자동 덮어쓰기 저장 여부"
    ),
    save_file: bool = typer.Option(
        False, "--save-file/--no-save-file", help="로컬 백업 파일(data/ 폴더) 저장 여부"
    ),
):
    """
    feeds.yaml 에 정의된 RSS 피드를 수집합니다.
    """
    console.print("[bold blue]RSS 피드 뉴스 수집 실행...[/bold blue]")
    asyncio.run(_run_target_scrapers(["rss_news"], format, sheets, save_file))


@app.command("run-portal")
def run_portal(
    format: str = typer.Option(
        settings.EXPORT_FORMAT, "--format", "-f", help="파일 저장 포맷 (json, jsonl, csv)"
    ),
    sheets: bool = typer.Option(
        True, "--sheets/--no-sheets", help="구글 스프레드시트 자동 덮어쓰기 저장 여부"
    ),
    save_file: bool = typer.Option(
        False, "--save-file/--no-save-file", help="로컬 백업 파일(data/ 폴더) 저장 여부"
    ),
):
    """
    portal.yaml 에 정의된 포털 사이트 공지/소식을 수집합니다.
    """
    console.print("[bold blue]포털 사이트 크롤링 수집 실행...[/bold blue]")
    asyncio.run(_run_target_scrapers(["portal_news"], format, sheets, save_file))


@app.command("run")
def run_scraper(
    name: str = typer.Argument(..., help="실행할 스크래퍼 이름 (예: rss_news, portal_news)"),
    format: str = typer.Option(
        settings.EXPORT_FORMAT, "--format", "-f", help="파일 저장 포맷 (json, jsonl, csv)"
    ),
    sheets: bool = typer.Option(
        True, "--sheets/--no-sheets", help="구글 스프레드시트 자동 덮어쓰기 저장 여부"
    ),
    save_file: bool = typer.Option(
        False, "--save-file/--no-save-file", help="로컬 백업 파일(data/ 폴더) 저장 여부"
    ),
):
    """
    지정한 개별 스크래퍼를 실행합니다.
    """
    console.print(f"[bold blue]'{name}' 스크래퍼 실행 중...[/bold blue]")
    asyncio.run(_run_target_scrapers([name], format, sheets, save_file))


@app.command("run-all")
def run_all_scrapers(
    format: str = typer.Option(
        settings.EXPORT_FORMAT, "--format", "-f", help="파일 저장 포맷 (json, jsonl, csv)"
    ),
    sheets: bool = typer.Option(
        True, "--sheets/--no-sheets", help="구글 스프레드시트 자동 덮어쓰기 저장 여부"
    ),
    save_file: bool = typer.Option(
        False, "--save-file/--no-save-file", help="로컬 백업 파일(data/ 폴더) 저장 여부"
    ),
):
    """
    RSS 피드와 포털 크롤러를 모두 포함하여 전체 수집을 실행합니다.
    """
    console.print("[bold blue]전체 뉴스 수집 시작...[/bold blue]")
    all_names = [s.name for s in scraper_registry.get_all_scrapers()]
    asyncio.run(_run_target_scrapers(all_names, format, sheets, save_file))


if __name__ == "__main__":
    app()
