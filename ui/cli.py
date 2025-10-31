"""Command-line interface for Backpack CLI Bot."""

import os
import sys
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from datetime import datetime

from api.backpack import BackpackClient
from core.order_manager import OrderManager
from core.position_manager import PositionManager
from core.risk_manager import RiskManager
from utils.helpers import (
    format_price, format_quantity, format_percentage,
    format_currency, color_pnl, parse_order_input
)
from config import config


class CLI:
    """Command-line interface for trading bot."""

    def __init__(self, client: BackpackClient):
        """Initialize CLI.

        Args:
            client: Backpack API client
        """
        self.client = client
        self.console = Console()
        self.order_manager = OrderManager(client)
        self.position_manager = PositionManager(client)
        self.risk_manager = RiskManager()

        self.current_symbol = config.DEFAULT_SYMBOL
        self.running = False
        self.current_price = 0.0

        # Key bindings
        self.kb = KeyBindings()
        self.setup_keybindings()

    def setup_keybindings(self):
        """Setup keyboard shortcuts."""
        # These will be used in the main loop
        pass

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name != 'nt' else 'cls')

    def display_header(self) -> Panel:
        """Create header panel.

        Returns:
            Rich Panel with header info
        """
        portfolio_value = self.position_manager.get_portfolio_value()
        total_pnl = self.position_manager.get_total_pnl()
        pnl_color = color_pnl(total_pnl)

        header_text = Text()
        header_text.append("Backpack CLI Bot", style="bold cyan")
        header_text.append(f" | Symbol: ", style="white")
        header_text.append(f"{self.current_symbol}", style="bold yellow")
        header_text.append(f" | Price: ", style="white")
        header_text.append(f"${format_price(self.current_price)}", style="bold white")
        header_text.append(f" | Portfolio: ", style="white")
        header_text.append(f"{format_currency(portfolio_value)}", style="bold green")
        header_text.append(f" | PnL: ", style="white")
        header_text.append(f"{format_currency(total_pnl)}", style=f"bold {pnl_color}")

        return Panel(header_text, border_style="blue")

    def display_positions(self) -> Table:
        """Create positions table.

        Returns:
            Rich Table with positions
        """
        table = Table(title="Positions", show_header=True, header_style="bold magenta")
        table.add_column("Symbol", style="cyan")
        table.add_column("Side", style="white")
        table.add_column("Quantity", justify="right")
        table.add_column("Entry", justify="right")
        table.add_column("Mark", justify="right")
        table.add_column("PnL", justify="right")
        table.add_column("PnL %", justify="right")

        positions = self.position_manager.get_all_positions()

        if not positions:
            table.add_row("No positions", "-", "-", "-", "-", "-", "-")
        else:
            for pos in positions:
                pnl_color = color_pnl(pos.unrealized_pnl)
                table.add_row(
                    pos.symbol,
                    pos.side,
                    format_quantity(pos.quantity),
                    format_price(pos.entry_price),
                    format_price(pos.mark_price),
                    f"[{pnl_color}]{format_currency(pos.unrealized_pnl)}[/{pnl_color}]",
                    f"[{pnl_color}]{format_percentage(pos.pnl_percentage)}[/{pnl_color}]"
                )

        return table

    def display_orders(self) -> Table:
        """Create orders table.

        Returns:
            Rich Table with open orders
        """
        table = Table(title="Open Orders", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim")
        table.add_column("Symbol", style="cyan")
        table.add_column("Side", style="white")
        table.add_column("Type", style="white")
        table.add_column("Quantity", justify="right")
        table.add_column("Price", justify="right")
        table.add_column("Filled", justify="right")

        orders = self.order_manager.get_open_orders()

        if not orders:
            table.add_row("No open orders", "-", "-", "-", "-", "-", "-")
        else:
            for order in orders:
                table.add_row(
                    order.order_id[:8],
                    order.symbol,
                    order.side,
                    order.order_type,
                    format_quantity(order.quantity),
                    format_price(order.price),
                    f"{format_percentage(order.fill_percentage)}"
                )

        return table

    def display_balances(self) -> Table:
        """Create balances table.

        Returns:
            Rich Table with balances
        """
        table = Table(title="Balances", show_header=True, header_style="bold magenta")
        table.add_column("Asset", style="cyan")
        table.add_column("Free", justify="right", style="green")
        table.add_column("Locked", justify="right", style="yellow")
        table.add_column("Total", justify="right", style="white")

        if not self.position_manager.balances:
            table.add_row("No balances", "-", "-", "-")
        else:
            for asset, balance in self.position_manager.balances.items():
                if balance["total"] > 0:  # Only show non-zero balances
                    table.add_row(
                        asset,
                        format_quantity(balance["free"]),
                        format_quantity(balance["locked"]),
                        format_quantity(balance["total"])
                    )

        return table

    def display_help(self) -> Panel:
        """Create help panel.

        Returns:
            Rich Panel with keyboard shortcuts
        """
        help_text = Text()
        help_text.append("Keyboard Shortcuts:\n", style="bold yellow")
        help_text.append("b - Buy market | ", style="green")
        help_text.append("s - Sell market | ", style="red")
        help_text.append("l - Limit buy | ", style="cyan")
        help_text.append("k - Limit sell\n", style="magenta")
        help_text.append("tb - Tiered buy | ", style="bold cyan")
        help_text.append("ts - Tiered sell\n", style="bold magenta")
        help_text.append("p - Refresh positions | ", style="white")
        help_text.append("o - Refresh orders | ", style="white")
        help_text.append("c - Cancel all orders\n", style="white")
        help_text.append("cr - Cancel price range | ", style="yellow")
        help_text.append("sym - Change symbol | ", style="yellow")
        help_text.append("r - Refresh all\n", style="white")
        help_text.append("h - Show help | ", style="white")
        help_text.append("q - Quit", style="white")

        return Panel(help_text, title="Help", border_style="yellow")

    def refresh_data(self):
        """Refresh all data from API."""
        try:
            # Refresh positions
            self.position_manager.refresh_positions()
            self.position_manager.refresh_balances()

            # Refresh orders
            self.order_manager.refresh_open_orders()

            # Get current price
            ticker = self.client.get_ticker(self.current_symbol)
            self.current_price = float(ticker.get("lastPrice", 0))

        except Exception as e:
            self.console.print(f"[red]Error refreshing data: {e}[/red]")

    def display_dashboard(self):
        """Display main dashboard."""
        self.clear_screen()

        # Display header
        self.console.print(self.display_header())
        self.console.print()

        # Display positions
        self.console.print(self.display_positions())
        self.console.print()

        # Display orders
        self.console.print(self.display_orders())
        self.console.print()

        # Display balances
        self.console.print(self.display_balances())
        self.console.print()

        # Display help
        self.console.print(self.display_help())

    def handle_buy_market(self):
        """Handle market buy order."""
        try:
            quantity_str = self.console.input("[green]Enter quantity to buy: [/green]")
            input_data = parse_order_input(quantity_str)
            quantity = input_data["quantity"]

            if quantity <= 0:
                self.console.print("[red]Invalid quantity[/red]")
                return

            # Validate order
            portfolio_value = self.position_manager.get_portfolio_value()
            is_valid, msg = self.risk_manager.validate_order(
                self.current_symbol, "Bid", quantity, self.current_price,
                self.position_manager.positions, portfolio_value
            )

            if not is_valid:
                self.console.print(f"[red]Order validation failed: {msg}[/red]")
                return

            # Place order
            order = self.order_manager.buy_market(self.current_symbol, quantity)
            if order:
                self.console.print(f"[green]Market buy order placed: {order}[/green]")
            else:
                self.console.print("[red]Failed to place order[/red]")

        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")

        self.console.input("\nPress Enter to continue...")

    def handle_sell_market(self):
        """Handle market sell order."""
        try:
            quantity_str = self.console.input("[red]Enter quantity to sell: [/red]")
            input_data = parse_order_input(quantity_str)
            quantity = input_data["quantity"]

            if quantity <= 0:
                self.console.print("[red]Invalid quantity[/red]")
                return

            # Validate order
            portfolio_value = self.position_manager.get_portfolio_value()
            is_valid, msg = self.risk_manager.validate_order(
                self.current_symbol, "Ask", quantity, self.current_price,
                self.position_manager.positions, portfolio_value
            )

            if not is_valid:
                self.console.print(f"[red]Order validation failed: {msg}[/red]")
                return

            # Place order
            order = self.order_manager.sell_market(self.current_symbol, quantity)
            if order:
                self.console.print(f"[green]Market sell order placed: {order}[/green]")
            else:
                self.console.print("[red]Failed to place order[/red]")

        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")

        self.console.input("\nPress Enter to continue...")

    def handle_buy_limit(self):
        """Handle limit buy order."""
        try:
            input_str = self.console.input("[cyan]Enter quantity@price (e.g., 10@100.5): [/cyan]")
            input_data = parse_order_input(input_str)
            quantity = input_data["quantity"]
            price = input_data["price"]

            if quantity <= 0 or not price or price <= 0:
                self.console.print("[red]Invalid quantity or price[/red]")
                return

            # Validate order
            portfolio_value = self.position_manager.get_portfolio_value()
            is_valid, msg = self.risk_manager.validate_order(
                self.current_symbol, "Bid", quantity, price,
                self.position_manager.positions, portfolio_value
            )

            if not is_valid:
                self.console.print(f"[red]Order validation failed: {msg}[/red]")
                return

            # Place order
            order = self.order_manager.buy_limit(self.current_symbol, quantity, price)
            if order:
                self.console.print(f"[green]Limit buy order placed: {order}[/green]")
            else:
                self.console.print("[red]Failed to place order[/red]")

        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")

        self.console.input("\nPress Enter to continue...")

    def handle_sell_limit(self):
        """Handle limit sell order."""
        try:
            input_str = self.console.input("[magenta]Enter quantity@price (e.g., 10@100.5): [/magenta]")
            input_data = parse_order_input(input_str)
            quantity = input_data["quantity"]
            price = input_data["price"]

            if quantity <= 0 or not price or price <= 0:
                self.console.print("[red]Invalid quantity or price[/red]")
                return

            # Validate order
            portfolio_value = self.position_manager.get_portfolio_value()
            is_valid, msg = self.risk_manager.validate_order(
                self.current_symbol, "Ask", quantity, price,
                self.position_manager.positions, portfolio_value
            )

            if not is_valid:
                self.console.print(f"[red]Order validation failed: {msg}[/red]")
                return

            # Place order
            order = self.order_manager.sell_limit(self.current_symbol, quantity, price)
            if order:
                self.console.print(f"[green]Limit sell order placed: {order}[/green]")
            else:
                self.console.print("[red]Failed to place order[/red]")

        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")

        self.console.input("\nPress Enter to continue...")

    def handle_cancel_all(self):
        """Handle cancel all orders."""
        try:
            confirm = self.console.input(f"[yellow]Cancel all orders for {self.current_symbol}? (y/n): [/yellow]")
            if confirm.lower() == 'y':
                success = self.order_manager.cancel_all_orders(self.current_symbol)
                if success:
                    self.console.print("[green]All orders cancelled[/green]")
                else:
                    self.console.print("[red]Failed to cancel orders[/red]")
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")

        self.console.input("\nPress Enter to continue...")

    def handle_cancel_price_range(self):
        """Handle cancel orders in price range."""
        try:
            self.console.print(f"[bold yellow]Cancel Orders in Price Range - {self.current_symbol}[/bold yellow]")
            self.console.print(f"Current price: ${format_price(self.current_price)}\n")

            # Get upper price bound
            upper_str = self.console.input("[yellow]Enter upper price bound: [/yellow]")
            price_high = float(upper_str.strip())

            # Get lower price bound
            lower_str = self.console.input("[yellow]Enter lower price bound: [/yellow]")
            price_low = float(lower_str.strip())

            if price_low <= 0 or price_high <= 0:
                self.console.print("[red]Prices must be greater than 0[/red]")
                self.console.input("\nPress Enter to continue...")
                return

            if price_low >= price_high:
                self.console.print("[red]Lower price must be less than upper price[/red]")
                self.console.input("\nPress Enter to continue...")
                return

            # Show preview of orders that will be cancelled
            orders_in_range = [
                order for order in self.order_manager.get_open_orders(self.current_symbol)
                if price_low <= order.price <= price_high
            ]

            if not orders_in_range:
                self.console.print(f"\n[yellow]No orders found in price range ${price_low:.4f} - ${price_high:.4f}[/yellow]")
                self.console.input("\nPress Enter to continue...")
                return

            # Display orders to be cancelled
            self.console.print(f"\n[bold]Orders to be cancelled:[/bold]")
            for order in orders_in_range:
                self.console.print(f"  {order.side} {order.quantity:.4f} @ ${order.price:.4f} (ID: {order.order_id[:8]})")

            # Confirm cancellation
            confirm = self.console.input(f"\n[yellow]Cancel {len(orders_in_range)} order(s)? (y/n): [/yellow]")
            if confirm.lower() != 'y':
                self.console.print("[yellow]Cancelled[/yellow]")
                self.console.input("\nPress Enter to continue...")
                return

            # Cancel orders
            successful, total = self.order_manager.cancel_orders_in_price_range(
                self.current_symbol, price_low, price_high
            )

            if successful == total:
                self.console.print(f"\n[bold green]Successfully cancelled {successful}/{total} orders[/bold green]")
            else:
                self.console.print(f"\n[bold yellow]Cancelled {successful}/{total} orders[/bold yellow]")

        except ValueError:
            self.console.print("[red]Invalid input. Please enter valid numbers.[/red]")
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")

        self.console.input("\nPress Enter to continue...")

    def handle_change_symbol(self):
        """Handle symbol change."""
        new_symbol = self.console.input("[yellow]Enter new symbol (e.g., BTC_USDC): [/yellow]")
        new_symbol = new_symbol.strip().upper()

        if "_" in new_symbol:
            self.current_symbol = new_symbol
            self.console.print(f"[green]Symbol changed to {self.current_symbol}[/green]")
            self.refresh_data()
        else:
            self.console.print("[red]Invalid symbol format. Use format: BASE_QUOTE[/red]")

        self.console.input("\nPress Enter to continue...")

    def handle_tiered_buy(self):
        """Handle tiered buy orders."""
        try:
            self.console.print("[bold cyan]Tiered Buy Orders[/bold cyan]")
            self.console.print(f"Current price: ${format_price(self.current_price)}\n")

            # Get parameters
            total_value_str = self.console.input("[green]Total value to buy (USD): [/green]")
            total_value = float(total_value_str.strip())

            price_low_str = self.console.input("[green]Lower price bound: [/green]")
            price_low = float(price_low_str.strip())

            price_high_str = self.console.input("[green]Upper price bound: [/green]")
            price_high = float(price_high_str.strip())

            num_orders_str = self.console.input("[green]Number of orders: [/green]")
            num_orders = int(num_orders_str.strip())

            if total_value <= 0 or price_low <= 0 or price_high <= 0 or num_orders <= 0:
                self.console.print("[red]All values must be greater than 0[/red]")
                self.console.input("\nPress Enter to continue...")
                return

            if price_low >= price_high:
                self.console.print("[red]Lower price must be less than upper price[/red]")
                self.console.input("\nPress Enter to continue...")
                return

            # Show preview
            self.console.print(f"\n[bold]Preview:[/bold]")
            self.console.print(f"Total: ${total_value:.2f}")
            self.console.print(f"Range: ${price_low:.4f} - ${price_high:.4f}")
            self.console.print(f"Orders: {num_orders}")
            self.console.print(f"Per order: ~${total_value/num_orders:.2f}\n")

            confirm = self.console.input("[yellow]Confirm? (y/n): [/yellow]")
            if confirm.lower() != 'y':
                self.console.print("[yellow]Cancelled[/yellow]")
                self.console.input("\nPress Enter to continue...")
                return

            # Place orders
            orders = self.order_manager.tiered_buy(
                self.current_symbol, total_value, price_low, price_high, num_orders
            )

            successful = sum(1 for o in orders if o is not None)
            self.console.print(f"\n[bold green]Placed {successful}/{num_orders} orders successfully[/bold green]")

        except ValueError:
            self.console.print("[red]Invalid input. Please enter valid numbers.[/red]")
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")

        self.console.input("\nPress Enter to continue...")

    def handle_tiered_sell(self):
        """Handle tiered sell orders."""
        try:
            self.console.print("[bold magenta]Tiered Sell Orders[/bold magenta]")
            self.console.print(f"Current price: ${format_price(self.current_price)}\n")

            # Get parameters
            total_quantity_str = self.console.input("[red]Total quantity to sell (SOL): [/red]")
            total_quantity = float(total_quantity_str.strip())

            price_low_str = self.console.input("[red]Lower price bound: [/red]")
            price_low = float(price_low_str.strip())

            price_high_str = self.console.input("[red]Upper price bound: [/red]")
            price_high = float(price_high_str.strip())

            num_orders_str = self.console.input("[red]Number of orders: [/red]")
            num_orders = int(num_orders_str.strip())

            if total_quantity <= 0 or price_low <= 0 or price_high <= 0 or num_orders <= 0:
                self.console.print("[red]All values must be greater than 0[/red]")
                self.console.input("\nPress Enter to continue...")
                return

            if price_low >= price_high:
                self.console.print("[red]Lower price must be less than upper price[/red]")
                self.console.input("\nPress Enter to continue...")
                return

            # Calculate approximate average price for total value display
            avg_price = (price_low + price_high) / 2
            total_value = total_quantity * avg_price

            # Show preview
            self.console.print(f"\n[bold]Preview:[/bold]")
            self.console.print(f"Total quantity: {total_quantity:.4f} SOL")
            self.console.print(f"Approx value: ${total_value:.2f} (at avg price ${avg_price:.2f})")
            self.console.print(f"Range: ${price_low:.4f} - ${price_high:.4f}")
            self.console.print(f"Orders: {num_orders}")
            self.console.print(f"Per order: ~{total_quantity/num_orders:.4f} SOL\n")

            confirm = self.console.input("[yellow]Confirm? (y/n): [/yellow]")
            if confirm.lower() != 'y':
                self.console.print("[yellow]Cancelled[/yellow]")
                self.console.input("\nPress Enter to continue...")
                return

            # Place orders using total quantity instead of total value
            orders = self.order_manager.tiered_sell_by_quantity(
                self.current_symbol, total_quantity, price_low, price_high, num_orders
            )

            successful = sum(1 for o in orders if o is not None)
            self.console.print(f"\n[bold green]Placed {successful}/{num_orders} orders successfully[/bold green]")

        except ValueError:
            self.console.print("[red]Invalid input. Please enter valid numbers.[/red]")
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")

        self.console.input("\nPress Enter to continue...")

    def run(self):
        """Run the CLI interface."""
        self.running = True

        # Validate configuration
        if not config.validate():
            self.console.print("[red]Error: API credentials not configured![/red]")
            self.console.print("[yellow]Please set BACKPACK_API_KEY and BACKPACK_API_SECRET in .env file[/yellow]")
            return

        self.console.print("[cyan]Starting Backpack CLI Bot...[/cyan]")
        self.refresh_data()

        while self.running:
            self.display_dashboard()

            # Get user command
            command = self.console.input("\n[bold cyan]Command: [/bold cyan]").strip().lower()

            if command == 'b':
                self.handle_buy_market()
            elif command == 's':
                self.handle_sell_market()
            elif command == 'l':
                self.handle_buy_limit()
            elif command == 'k':
                self.handle_sell_limit()
            elif command == 'tb':
                self.handle_tiered_buy()
            elif command == 'ts':
                self.handle_tiered_sell()
            elif command == 'p':
                self.position_manager.refresh_positions()
                self.console.print("[green]Positions refreshed[/green]")
                self.console.input("\nPress Enter to continue...")
            elif command == 'o':
                self.order_manager.refresh_open_orders()
                self.console.print("[green]Orders refreshed[/green]")
                self.console.input("\nPress Enter to continue...")
            elif command == 'c':
                self.handle_cancel_all()
            elif command == 'cr':
                self.handle_cancel_price_range()
            elif command == 'sym':
                self.handle_change_symbol()
            elif command == 'r':
                self.refresh_data()
                self.console.print("[green]All data refreshed[/green]")
                self.console.input("\nPress Enter to continue...")
            elif command == 'h':
                self.console.input("\nPress Enter to continue...")
            elif command == 'q':
                self.running = False
                self.console.print("[cyan]Goodbye![/cyan]")
            else:
                self.console.print("[red]Unknown command. Press 'h' for help.[/red]")
                self.console.input("\nPress Enter to continue...")
