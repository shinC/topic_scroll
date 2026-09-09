import asyncio
import sys
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table

from config import settings
from pipeline.exporter import ArticleExporter
from pipeline.processor import ArticleProcessor
from scrapers.registry import scraper_registry
from utils.http_client import get_http_client
from utils.logger import logger

app = typer.Typer(
    help="topic_scroll: 파이썬 3.14 기반 각종 뉴스 사이트 비동기 스크래퍼 CLI",
    add_completion=False
)
console = Console()


@app.callback()
def main_callback():
    """스크래퍼 자동 등록 및 환경 구성을 초기화합니다."""
    scraper_registry.auto_discover()


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
    console.print(f"\n총 [bold yellow]{len(scrapers)}[/bold yellow]개의 스크래퍼가 등록되어 있습니다.")


async def _run_single(scraper_name: str, export_format: str):
    """단일 스크래퍼 비동기 실행 내부 함수"""
    try:
        scraper = scraper_registry.get_scraper(scraper_name)
    except KeyError as e:
        console.print(f"[bold red]오류:[/bold red] {str(e)}")
        sys.exit(1)

    async with get_http_client() as client:
        result = await scraper.run(client=client)

    if result.success and result.articles:
        processor = ArticleProcessor()
        result.articles = processor.process(result.articles)
        result.total_count = len(result.articles)

        exporter = ArticleExporter()
        output_file = exporter.export_result(result, format_type=export_format)
        console.print(f"[bold green]수집 성공![/bold green] 기사 {result.total_count}개 저장 완료 -> [cyan]{output_file}[/cyan]")
    else:
        console.print(f"[bold red]수집 실패:[/bold red] {result.error_message or '기사를 찾을 수 없습니다.'}")


@app.command("run")
def run_scraper(
    name: str = typer.Argument(..., help="실행할 스크래퍼 이름 (예: sample_news)"),
    format: str = typer.Option(settings.EXPORT_FORMAT, "--format", "-f", help="저장 포맷 (json, jsonl, csv)")
):
    """
    지정한 단일 뉴스 사이트 스크래퍼를 실행합니다.
    """
    console.print(f"[bold blue]'{name}' 스크래퍼 실행 중...[/bold blue]")
    asyncio.run(_run_single(name, format))


async def _run_all(export_format: str):
    """전체 스크래퍼 비동기 동시 실행 내부 함수"""
    scrapers = scraper_registry.get_all_scrapers()
    if not scrapers:
        console.print("[bold yellow]등록된 스크래퍼가 없습니다.[/bold yellow]")
        return

    console.print(f"[bold blue]총 {len(scrapers)}개 스크래퍼 동시 수집 시작...[/bold blue]")
    
    async with get_http_client() as client:
        tasks = [scraper.run(client=client) for scraper in scrapers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    exporter = ArticleExporter()
    processor = ArticleProcessor()

    total_articles = 0
    for res in results:
        if isinstance(res, Exception):
            logger.error(f"스크래퍼 실행 오류: {str(res)}")
            continue

        if res.success and res.articles:
            res.articles = processor.process(res.articles)
            res.total_count = len(res.articles)
            output_file = exporter.export_result(res, format_type=export_format)
            total_articles += res.total_count
            console.print(f" - [{res.site_name}] {res.total_count}개 기사 저장: [cyan]{output_file}[/cyan]")
        else:
            console.print(f" - [{res.site_name}] 수집 실패: {res.error_message}")

    console.print(f"\n[bold green]전체 수집 완료![/bold green] 총 [bold yellow]{total_articles}[/bold yellow]개 기사 수집됨.")


@app.command("run-all")
def run_all_scrapers(
    format: str = typer.Option(settings.EXPORT_FORMAT, "--format", "-f", help="저장 포맷 (json, jsonl, csv)")
):
    """
    등록된 모든 뉴스 사이트 스크래퍼를 동시 비동기 실행합니다.
    """
    asyncio.run(_run_all(format))


if __name__ == "__main__":
    app()
