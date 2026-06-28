import sys
import os
import time
from datetime import datetime

os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/clean", exist_ok=True)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
    from rich.text import Text
    from rich.columns import Columns
    from rich.rule import Rule
    from rich.align import Align
    from rich import box
    from rich.live import Live
    from rich.layout import Layout
    from rich.syntax import Syntax
except ImportError:
    print("Installing rich...")
    os.system("pip install rich --break-system-packages -q")
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
    from rich.text import Text
    from rich.columns import Columns
    from rich.rule import Rule
    from rich.align import Align
    from rich import box
    from rich.live import Live
    from rich.layout import Layout
    from rich.syntax import Syntax

console = Console()

BRAND = "[bold cyan]E[/bold cyan][bold blue]─[/bold blue][bold cyan]Commerce Analytics[/bold cyan]"
VERSION = "v1.0"

THEME = {
    "primary": "bold cyan",
    "secondary": "dim cyan",
    "success": "bold green",
    "error": "bold red",
    "warning": "bold yellow",
    "info": "bold blue",
    "muted": "dim white",
    "accent": "magenta",
}


def cls():
    console.clear()


def banner():
    cls()
    art = """
  ███████╗      ██████╗ ██████╗ ███╗   ███╗███╗   ███╗███████╗██████╗  ██████╗███████╗
  ██╔════╝     ██╔════╝██╔═══██╗████╗ ████║████╗ ████║██╔════╝██╔══██╗██╔════╝██╔════╝
  █████╗ █████╗██║     ██║   ██║██╔████╔██║██╔████╔██║█████╗  ██████╔╝██║     █████╗  
  ██╔══╝ ╚════╝██║     ██║   ██║██║╚██╔╝██║██║╚██╔╝██║██╔══╝  ██╔══██╗██║     ██╔══╝  
  ███████╗     ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║ ╚═╝ ██║███████╗██║  ██║╚██████╗███████╗
  ╚══════╝      ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚══════╝"""

    console.print(art, style="bold cyan", highlight=False)
    console.print(
        Align.center(
            Text.from_markup(
                f"  [dim]Order Analytics System[/dim]  [bold white]·[/bold white]  "
                f"[dim]{VERSION}[/dim]  [bold white]·[/bold white]  "
                f"[dim]Python + SQLite[/dim]"
            )
        )
    )
    console.print()


def section(title, subtitle=None):
    console.print()
    console.print(Rule(f"[bold cyan] {title} [/bold cyan]", style="cyan"))
    if subtitle:
        console.print(Align.center(f"[dim]{subtitle}[/dim]"))
    console.print()


def success(msg):
    console.print(f"  [bold green]✓[/bold green]  {msg}")


def error(msg):
    console.print(f"  [bold red]✗[/bold red]  {msg}")


def info(msg):
    console.print(f"  [bold blue]ℹ[/bold blue]  {msg}")


def warn(msg):
    console.print(f"  [bold yellow]⚠[/bold yellow]  {msg}")


def stat_card(label, value, color="cyan"):
    return Panel(
        Align.center(f"[bold {color}]{value}[/bold {color}]\n[dim]{label}[/dim]"),
        border_style=color,
        padding=(0, 2),
    )


def fmt_currency(val):
    if val is None:
        return "[dim]N/A[/dim]"
    try:
        return f"[green]₹{float(val):,.2f}[/green]"
    except Exception:
        return str(val)


def fmt_pct(val, invert=False):
    if val is None:
        return "[dim]N/A[/dim]"
    try:
        v = float(val)
        if invert:
            v = -v
        color = "green" if v >= 0 else "red"
        arrow = "▲" if v >= 0 else "▼"
        return f"[{color}]{arrow} {abs(v):.2f}%[/{color}]"
    except Exception:
        return str(val)


def make_table(title, columns, rows, col_styles=None):
    t = Table(
        title=f"[bold cyan]{title}[/bold cyan]",
        box=box.ROUNDED,
        border_style="cyan",
        header_style="bold cyan",
        show_lines=False,
        expand=False,
    )
    for i, col in enumerate(columns):
        style = col_styles[i] if col_styles and i < len(col_styles) else "white"
        t.add_column(col, style=style)
    for row in rows:
        t.add_row(*[str(v) if v is not None else "[dim]—[/dim]" for v in row])
    return t


def spinner_task(msg, fn, *args, **kwargs):
    with Progress(
        SpinnerColumn(style="cyan"),
        TextColumn(f"[cyan]{msg}[/cyan]"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as prog:
        prog.add_task("", total=None)
        result = fn(*args, **kwargs)
    return result


def menu_setup():
    section("SETUP WIZARD", "Initialize the E-Commerce Analytics System")

    panels = [
        Panel("[bold]Step 1[/bold]\n[dim]Generate CSV data[/dim]", border_style="blue", padding=(0, 2)),
        Panel("[bold]Step 2[/bold]\n[dim]Clean & validate[/dim]", border_style="yellow", padding=(0, 2)),
        Panel("[bold]Step 3[/bold]\n[dim]Load into SQLite[/dim]", border_style="green", padding=(0, 2)),
    ]
    console.print(Columns(panels, equal=True, expand=True))
    console.print()

    if not Confirm.ask("  [cyan]Run full setup?[/cyan]", default=True):
        return

    console.print()
    from generate_data import generate_all
    from clean_data import run_all_cleaning
    from queries import load_data_to_db

    with Progress(
        SpinnerColumn(style="bold cyan"),
        TextColumn("[cyan]{task.description}[/cyan]"),
        BarColumn(bar_width=30, style="cyan", complete_style="bold green"),
        TextColumn("[bold]{task.percentage:>3.0f}%[/bold]"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Generating data...", total=3)

        progress.update(task, description="[cyan]Generating CSV files...[/cyan]")
        nc, np_, no, ni = generate_all()
        progress.advance(task)
        time.sleep(0.3)

        progress.update(task, description="[cyan]Cleaning & validating...[/cyan]")
        issues, stats, report_path = run_all_cleaning()
        progress.advance(task)
        time.sleep(0.3)

        progress.update(task, description="[cyan]Loading into SQLite...[/cyan]")
        db_counts = load_data_to_db()
        progress.advance(task)
        time.sleep(0.3)

    console.print()
    cards = [
        stat_card("Customers", nc, "blue"),
        stat_card("Products", np_, "magenta"),
        stat_card("Orders", no, "cyan"),
        stat_card("Items", ni, "green"),
    ]
    console.print(Columns(cards, equal=True, expand=True))
    console.print()

    issue_color = "yellow" if issues else "green"
    console.print(
        Panel(
            f"[{issue_color}]Issues found: {len(issues)}[/{issue_color}]\n"
            f"[dim]Report saved → {report_path}[/dim]",
            title="[bold]Cleaning Summary[/bold]",
            border_style=issue_color,
        )
    )

    if issues and Confirm.ask("\n  [cyan]View issue log?[/cyan]", default=False):
        t = Table(box=box.SIMPLE, header_style="bold yellow", show_lines=False)
        t.add_column("#", style="dim", width=4)
        t.add_column("Issue", style="yellow")
        for i, iss in enumerate(issues[:30], 1):
            t.add_row(str(i), iss)
        if len(issues) > 30:
            t.add_row("...", f"[dim]and {len(issues)-30} more (see {report_path})[/dim]")
        console.print(t)

    success("Setup complete! System ready for analysis.")
    console.input("\n  [dim]Press Enter to continue...[/dim]")


def display_query_results(title, rows, columns, col_styles=None, limit=25):
    if not rows:
        warn(f"No results returned for: {title}")
        return

    display_rows = rows[:limit]
    table_rows = [[r.get(c, "") for c in columns] for r in display_rows]
    t = make_table(title, columns, table_rows, col_styles)
    console.print(Align.center(t))

    if len(rows) > limit:
        info(f"Showing {limit} of {len(rows)} rows")
    success(f"{len(rows)} row(s) returned")


def menu_sql_queries():
    from queries import ALL_QUERIES

    QUERY_GROUPS = {
        "Basic Queries": {
            "q1": ("Total Revenue per Category", ["category", "total_revenue"]),
            "q2": ("Top 10 Customers by Value", ["customer_id", "customer_name", "total_value"]),
            "q3": ("Monthly Order Count (12 mo)", ["month", "order_count"]),
        },
        "Intermediate Queries": {
            "q4": ("Customers Never Delivered", ["customer_id", "customer_name"]),
            "q5": ("More Returns than Purchases", ["product_id", "product_name", "purchases", "returns"]),
            "q6": ("Return Rate per Category", ["category", "returned_items", "total_items", "return_rate_pct"]),
        },
        "Advanced — Window Functions": {
            "q7": ("Running Totals by Region", ["region_code", "order_date", "daily_revenue", "running_total"]),
            "q8": ("DENSE_RANK: Products by Category", ["category", "product_name", "total_revenue", "rank_in_category"]),
            "q9": ("LAG: Days Between Orders", ["customer_id", "order_date", "previous_order_date", "days_gap", "risk_flag"]),
        },
        "Advanced — CTEs & Analytics": {
            "q10": ("CTE Multi-level Revenue Buckets", ["month", "revenue_category", "customer_count"]),
            "q11": ("NTILE: Customer Segments", ["customer_id", "total_value", "quartile", "quartile_label"]),
            "q12": ("YoY Revenue Comparison", ["year", "month", "revenue", "prev_year_revenue", "yoy_growth_percent"]),
            "q13": ("First/Last Category Shift", ["customer_id", "first_category", "last_category", "category_shift"]),
            "q14": ("Cumulative Revenue Distribution", ["customer_id", "revenue", "cumulative_revenue", "cumulative_percent"]),
            "q15": ("Cohort Retention Analysis", ["cohort_month", "cohort_total", "months_since_join", "active_customers", "retention_rate"]),
            "q16": ("Products Bought Together", ["product_a_id", "product_a", "product_b_id", "product_b", "times_bought_together"]),
        },
    }

    while True:
        section("SQL ANALYSIS", "16 queries across Basic, Intermediate & Advanced levels")

        options = []
        flat_map = {}
        idx = 1
        for group, queries in QUERY_GROUPS.items():
            console.print(f"  [bold cyan]{group}[/bold cyan]")
            for qkey, (qlabel, _) in queries.items():
                console.print(f"    [dim]{idx:2d}.[/dim]  [white]{qlabel}[/white]  [dim]({qkey})[/dim]")
                flat_map[str(idx)] = (qkey, qlabel, QUERY_GROUPS)
                options.append(str(idx))
                idx += 1
            console.print()

        console.print("  [bold cyan]Special[/bold cyan]")
        console.print("    [dim]all[/dim]  Run all 16 queries")
        console.print("    [dim]  0[/dim]  Back to main menu")
        console.print()

        choice = Prompt.ask("  [cyan]Select query[/cyan]", default="0")

        if choice == "0":
            break

        if choice.lower() == "all":
            section("RUNNING ALL QUERIES")
            for qkey, (qlabel, fn) in ALL_QUERIES.items():
                cols = None
                for group, queries in QUERY_GROUPS.items():
                    if qkey in queries:
                        _, cols = queries[qkey]
                rows = spinner_task(f"Running {qlabel}...", fn)
                console.print()
                display_query_results(qlabel, rows, cols, limit=10)
                console.print()
            console.input("  [dim]Press Enter to continue...[/dim]")
            continue

        if choice not in flat_map:
            error("Invalid selection.")
            time.sleep(1)
            continue

        qkey, qlabel, _ = flat_map[choice]
        cols = None
        for group, queries in QUERY_GROUPS.items():
            if qkey in queries:
                _, cols = queries[qkey]

        fn = ALL_QUERIES[qkey][1]
        section(qlabel)
        rows = spinner_task(f"Executing {qlabel}...", fn)
        console.print()
        display_query_results(qlabel, rows, cols, limit=30)
        console.print()
        console.input("  [dim]Press Enter to continue...[/dim]")


def menu_report_generator():
    from report_generator import generate_report

    section("REPORT GENERATOR", "Generate period-based business summary reports")

    console.print("  [bold cyan]Report Types:[/bold cyan]")
    console.print("    [dim]1.[/dim]  Daily")
    console.print("    [dim]2.[/dim]  Weekly")
    console.print("    [dim]3.[/dim]  Monthly")
    console.print()

    rt_map = {"1": "daily", "2": "weekly", "3": "monthly"}
    rt_choice = Prompt.ask("  [cyan]Report type[/cyan]", choices=["1", "2", "3"], default="3")
    report_type = rt_map[rt_choice]

    console.print()
    console.print(f"  [dim]Enter date range (format: YYYY-MM-DD)[/dim]")

    while True:
        start_str = Prompt.ask("  [cyan]Start date[/cyan]", default="2024-01-01")
        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d")
            break
        except ValueError:
            error("Invalid date format. Use YYYY-MM-DD.")

    while True:
        end_str = Prompt.ask("  [cyan]End date[/cyan]", default="2024-12-31")
        try:
            end_date = datetime.strptime(end_str, "%Y-%m-%d")
            if end_date < start_date:
                error("End date must be after start date.")
                continue
            break
        except ValueError:
            error("Invalid date format. Use YYYY-MM-DD.")

    console.print()
    report = spinner_task("Generating report...", generate_report, report_type, start_date, end_date)

    console.print()
    section(f"{report_type.upper()} REPORT",
            f"{report['period']['start']}  →  {report['period']['end']}")

    curr = report["current"]
    prev = report["previous"]
    comp = report["comparison"]

    cards = [
        stat_card("Total Orders", curr["total_orders"] or 0, "cyan"),
        stat_card("Revenue", f"₹{(curr['revenue'] or 0):,.0f}", "green"),
        stat_card("Unique Customers", curr["unique_customers"] or 0, "blue"),
    ]
    console.print(Columns(cards, equal=True, expand=True))
    console.print()

    comp_table = Table(
        title="[bold cyan]Period Comparison[/bold cyan]",
        box=box.ROUNDED, border_style="cyan", header_style="bold cyan"
    )
    comp_table.add_column("Metric", style="white")
    comp_table.add_column("Current", style="cyan", justify="right")
    comp_table.add_column("Previous", style="dim", justify="right")
    comp_table.add_column("Change", justify="right")

    comp_table.add_row(
        "Orders",
        str(curr["total_orders"] or 0),
        str(prev["total_orders"] or 0),
        fmt_pct(comp["orders_change_pct"]),
    )
    comp_table.add_row(
        "Revenue",
        f"₹{(curr['revenue'] or 0):,.2f}",
        f"₹{(prev['revenue'] or 0):,.2f}",
        fmt_pct(comp["revenue_change_pct"]),
    )
    comp_table.add_row(
        "Customers",
        str(curr["unique_customers"] or 0),
        str(prev["unique_customers"] or 0),
        fmt_pct(comp["customers_change_pct"]),
    )
    console.print(Align.center(comp_table))
    console.print()

    if report["top_products"]:
        top_t = Table(
            title="[bold cyan]Top 3 Products[/bold cyan]",
            box=box.ROUNDED, border_style="cyan", header_style="bold cyan"
        )
        top_t.add_column("Rank", style="dim", width=6, justify="center")
        top_t.add_column("Product", style="white")
        top_t.add_column("Revenue", style="green", justify="right")
        top_t.add_column("Units Sold", style="cyan", justify="right")

        medals = ["🥇", "🥈", "🥉"]
        for i, p in enumerate(report["top_products"]):
            top_t.add_row(
                medals[i] if i < 3 else str(i + 1),
                str(p.get("product_name", "")),
                f"₹{(p.get('revenue') or 0):,.2f}",
                str(p.get("units_sold", 0)),
            )
        console.print(Align.center(top_t))
    else:
        warn("No product data available for this period.")

    console.print()
    prev_label = f"{report['prev_period']['start']} → {report['prev_period']['end']}"
    info(f"Previous period: [dim]{prev_label}[/dim]")
    console.input("\n  [dim]Press Enter to continue...[/dim]")


def menu_edge_cases():
    from edge_cases import run_all_tests

    section("EDGE CASE TESTS", "Validating system behaviour under anomalous data conditions")

    results = spinner_task("Running test suite...", run_all_tests)

    console.print()
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    color = "green" if passed == total else ("yellow" if passed > 0 else "red")

    console.print(
        Panel(
            Align.center(
                f"[bold {color}]{passed}/{total} Tests Passed[/bold {color}]"
            ),
            border_style=color,
            padding=(0, 4),
        )
    )
    console.print()

    for r in results:
        status_icon = "[bold green]✓ PASS[/bold green]" if r["passed"] else "[bold red]✗ FAIL[/bold red]"
        border = "green" if r["passed"] else "red"
        console.print(
            Panel(
                f"[bold white]{r['test']}[/bold white]\n\n"
                f"[dim]Detail:[/dim]  {r['detail']}\n"
                f"[dim]Expected:[/dim] [cyan]{r['expected']}[/cyan]\n"
                f"[dim]Got:[/dim]     [yellow]{r['got']}[/yellow]",
                title=status_icon,
                border_style=border,
                padding=(0, 2),
            )
        )
        console.print()

    console.input("  [dim]Press Enter to continue...[/dim]")


def menu_data_explorer():
    from queries import get_connection

    section("DATA EXPLORER", "Browse your raw database tables")

    tables = {
        "1": ("customers", ["customer_id", "customer_name", "email", "customer_type", "registration_date"]),
        "2": ("orders", ["order_id", "customer_id", "order_date", "status", "region_code"]),
        "3": ("order_items", ["item_id", "order_id", "product_id", "quantity", "unit_price", "discount_percent"]),
        "4": ("products", ["product_id", "product_name", "category", "subcategory", "cost_price"]),
    }

    for k, (tname, _) in tables.items():
        console.print(f"  [dim]{k}.[/dim]  [white]{tname}[/white]")
    console.print(f"  [dim]0.[/dim]  Back")
    console.print()

    choice = Prompt.ask("  [cyan]Select table[/cyan]", default="0")
    if choice == "0" or choice not in tables:
        return

    tname, cols = tables[choice]
    limit_str = Prompt.ask("  [cyan]Rows to display[/cyan]", default="20")
    try:
        limit = int(limit_str)
    except ValueError:
        limit = 20

    conn = get_connection()
    rows = conn.execute(f"SELECT * FROM {tname} LIMIT ?", (limit,)).fetchall()
    count = conn.execute(f"SELECT COUNT(*) FROM {tname}").fetchone()[0]
    conn.close()

    console.print()
    data = [dict(r) for r in rows]
    display_query_results(tname.upper(), data, cols, limit=limit)
    info(f"Table has [bold]{count}[/bold] total rows")
    console.input("\n  [dim]Press Enter to continue...[/dim]")


def main_menu():
    while True:
        banner()

        db_exists = os.path.exists("data/ecommerce.db")
        status_text = "[bold green]● Database ready[/bold green]" if db_exists else "[bold red]● Not initialized[/bold red]"

        console.print(
            Panel(
                Align.center(status_text),
                border_style="cyan" if db_exists else "red",
                padding=(0, 4),
            )
        )
        console.print()

        menu_items = [
            ("1", "Setup Wizard", "Generate data, clean, load into SQLite", "cyan"),
            ("2", "SQL Analysis", "Run all 16 analytical queries", "blue"),
            ("3", "Report Generator", "Period-based business reports", "green"),
            ("4", "Edge Case Tests", "Validate data integrity & anomalies", "yellow"),
            ("5", "Data Explorer", "Browse tables interactively", "magenta"),
            ("0", "Exit", "", "dim"),
        ]

        grid = Table.grid(expand=True)
        grid.add_column(width=6)
        grid.add_column()
        grid.add_column()

        for key, label, desc, color in menu_items:
            grid.add_row(
                f"  [dim]{key}.[/dim]",
                f"[bold {color}]{label}[/bold {color}]",
                f"  [dim]{desc}[/dim]" if desc else "",
            )

        console.print(
            Panel(grid, title="[bold cyan] MAIN MENU [/bold cyan]", border_style="cyan", padding=(1, 2))
        )
        console.print()

        choice = Prompt.ask("  [cyan]Select option[/cyan]", choices=["0", "1", "2", "3", "4", "5"])

        if choice == "0":
            cls()
            console.print(
                Panel(
                    Align.center("[bold cyan]Thanks for using E-Commerce Analytics![/bold cyan]\n[dim]Goodbye.[/dim]"),
                    border_style="cyan",
                    padding=(1, 4),
                )
            )
            console.print()
            sys.exit(0)

        if choice == "1":
            menu_setup()
        elif choice == "2":
            if not db_exists:
                error("Database not initialized. Run Setup Wizard first.")
                time.sleep(2)
            else:
                menu_sql_queries()
        elif choice == "3":
            if not db_exists:
                error("Database not initialized. Run Setup Wizard first.")
                time.sleep(2)
            else:
                menu_report_generator()
        elif choice == "4":
            menu_edge_cases()
        elif choice == "5":
            if not db_exists:
                error("Database not initialized. Run Setup Wizard first.")
                time.sleep(2)
            else:
                menu_data_explorer()


if __name__ == "__main__":
    main_menu()
