import React, { useMemo, useState, useEffect } from "react";
import { usePortfolioData } from "../hooks/usePortfolioData";
import { useEodHistory } from "../hooks/useEodHistory";
import { DataTable, useQuoteContext } from "@gzc/ui";
import { ContextMenu } from "@gzc/ui";
import type { PortfolioItem } from "../types/portfolio";
import type { ColumnDef } from "@tanstack/react-table";
import type { PortfolioFilter } from "../types/portfolio";
import { QuoteInput, QuoteMessage } from "@gzc/ui";

interface PortfolioTableProps {
    filters: PortfolioFilter;
}

const PortfolioTable: React.FC<PortfolioTableProps> = ({ filters }) => {
    const { portfolio, isLoading } = usePortfolioData(filters);
    const { latestQuotes } = useQuoteContext();

    const [contextMenu, setContextMenu] = useState<{
        x: number;
        y: number;
        value: PortfolioItem[keyof PortfolioItem] | null;
        row: PortfolioItem;
    } | null>(null);

    useEffect(() => {
        const hideMenu = () => setContextMenu(null);
        window.addEventListener("click", hideMenu);
        return () => window.removeEventListener("click", hideMenu);
    }, []);
    const handleRightClick = (
        e: React.MouseEvent,
        value: PortfolioItem[keyof PortfolioItem],
        row: PortfolioItem
    ) => {
        e.preventDefault();
        setContextMenu({
            x: e.clientX,
            y: e.clientY,
            value,
            row,
        });
    };

    const eodInputs = useMemo<QuoteInput[]>(
        () =>
            portfolio.map((pos) => ({
                symbol: pos.Symbol,
                entryType: pos.Side === "Buy" ? "ask" : "bid",
                tradeDate: pos.TradeDate,
                expirationDate: pos.ExpirationOrMaturityDate,
            })),
        [portfolio]
    );
    const { history } = useEodHistory(eodInputs);
    const getLatestQuote = (symbol: string, side: "ask" | "bid") =>
        latestQuotes[`${symbol}_${side}`]?.price ?? null;
    const getRefPrice = (
        tradeDate: string,
        cost: number,
        currentPrice: number,
        type: "YTD" | "MTD" | "DTD"
    ) => {
        const now = new Date();
        const trade = new Date(tradeDate);
        const useCost =
            (type === "YTD" && trade > new Date(now.getFullYear(), 0, 1)) ||
            (type === "MTD" &&
                trade > new Date(now.getFullYear(), now.getMonth(), 1)) ||
            (type === "DTD" &&
                trade >
                    new Date(now.getFullYear(), now.getMonth(), now.getDate()));
        return useCost ? cost : currentPrice;
    };
    const tableData = portfolio.map((pos) => {
        const symbol = pos.Symbol;
        const latestQuote = getLatestQuote(
            symbol,
            pos.Side == "2" ? "ask" : ("bid" as "ask" | "bid")
        ); // Assuming ask = sell
        const currentPrice = latestQuote;
        const ref = history[pos.Symbol];
        const side = pos.Side === "Buy" ? "ask" : "bid"; // Buy uses ask, Sell uses bid
        const sideRef = ref?.[side];

        return {
            ...pos,
            currentPrice,
            pnlYTD: sideRef?.ytd
                ? (currentPrice -
                      getRefPrice(
                          pos.TradeDate,
                          pos.Price,
                          sideRef.ytd,
                          "YTD"
                      )) *
                  pos.OrderQty
                : null,
            pnlMTD: sideRef?.mtd
                ? (currentPrice -
                      getRefPrice(
                          pos.TradeDate,
                          pos.Price,
                          sideRef.mtd,
                          "MTD"
                      )) *
                  pos.OrderQty
                : null,
            pnlDTD: sideRef?.dtd
                ? (currentPrice -
                      getRefPrice(
                          pos.TradeDate,
                          pos.Price,
                          sideRef.dtd,
                          "DTD"
                      )) *
                  pos.OrderQty
                : null,
        };
    });
    const columns: ColumnDef<(typeof tableData)[0]>[] = [
        { accessorKey: "OrderID", header: "Order ID" },
        { accessorKey: "Symbol", header: "Symbol" },
        { accessorKey: "Position", header: "Position" },
        { accessorKey: "OrderQty", header: "Qty" },
        { accessorKey: "Price", header: "Cost" },
        { accessorKey: "currentPrice", header: "Current Price" },
        {
            accessorKey: "pnlYTD",
            header: "YTD P&L",
            cell: (info) => {
                const value = info.getValue() as number | null;
                return value != null ? value.toFixed(2) : "-";
            },
        },
        {
            accessorKey: "pnlMTD",
            header: "MTD P&L",
            cell: (info) => {
                const value = info.getValue() as number | null;
                return value != null ? value.toFixed(2) : "-";
            },
        },
        {
            accessorKey: "pnlDTD",
            header: "DTD P&L",
            cell: (info) => {
                const value = info.getValue() as number | null;
                return value != null ? value.toFixed(2) : "-";
            },
        },
        { accessorKey: "TradeDate", header: "Trade Date" },
        { accessorKey: "CounterpartyID", header: "Counterparty" },
    ];
    return (
        <div className="p-4 relative">
            <DataTable
                data={tableData}
                columns={columns}
                isLoading={isLoading}
                onCellRightClick={handleRightClick}
            />

            {contextMenu && (
                <ContextMenu
                    x={contextMenu.x}
                    y={contextMenu.y}
                    onClose={() => setContextMenu(null)}
                >
                    <ContextMenu.Item
                        onClick={() =>
                            alert(`Inspecting: ${contextMenu.value}`)
                        }
                    >
                        🔍 Inspect
                    </ContextMenu.Item>
                    <ContextMenu.Submenu label="⚙️ Actions">
                        <ContextMenu.Item
                            onClick={() =>
                                alert(
                                    `Duplicate Order ${contextMenu.row.OrderID}`
                                )
                            }
                        >
                            🔁 Duplicate
                        </ContextMenu.Item>
                        <ContextMenu.Item
                            onClick={() =>
                                alert(`Flag ${contextMenu.row.Symbol}`)
                            }
                        >
                            🚩 Flag
                        </ContextMenu.Item>
                    </ContextMenu.Submenu>
                    <ContextMenu.Item
                        onClick={() =>
                            alert(`Delete ${contextMenu.row.Symbol}`)
                        }
                    >
                        ❌ Remove
                    </ContextMenu.Item>
                </ContextMenu>
            )}
        </div>
    );
};

export default PortfolioTable;
