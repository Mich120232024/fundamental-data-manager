import React from "react";
import { PortfolioFilter } from "../types/portfolio";
interface PortfolioFiltersProps {
    filters: PortfolioFilter;
    onFilterChange: (filters: PortfolioFilter) => void;
}
const PortfolioFilters: React.FC<PortfolioFiltersProps> = ({
    filters,
    onFilterChange,
}) => {
    const handleChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
    ) => {
        const { name, value } = e.target;
        onFilterChange({
            ...filters,
            [name]: value === "" ? undefined : value,
        });
    };

    return (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 border-b dark:border-gzc-light-black">
            <div>
                <label className="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">
                    Symbol
                </label>
                <input
                    type="text"
                    name="symbol"
                    value={filters.symbol || ""}
                    onChange={handleChange}
                    placeholder="e.g. EURUSD"
                    className="w-full border border-gray-300 dark:border-gray-600 rounded px-3 py-2 text-sm bg-white dark:bg-gzc-mid-black text-gray-900 dark:text-white"
                />
            </div>
            <div>
                <label className="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">
                    Fund ID
                </label>
                <input
                    type="number"
                    name="fundId"
                    value={filters.fundId ?? ""}
                    onChange={handleChange}
                    placeholder="e.g. 101"
                    className="w-full border border-gray-300 dark:border-gray-600 rounded px-3 py-2 text-sm bg-white dark:bg-gzc-mid-black text-gray-900 dark:text-white"
                />
            </div>
            <div>
                <label className="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">
                    Trader
                </label>
                <input
                    type="text"
                    name="trader"
                    value={filters.trader || ""}
                    onChange={handleChange}
                    placeholder="Trader Name"
                    className="w-full border border-gray-300 dark:border-gray-600 rounded px-3 py-2 text-sm bg-white dark:bg-gzc-mid-black text-gray-900 dark:text-white"
                />
            </div>
            <div>
                <label className="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">
                    Position
                </label>
                <input
                    type="text"
                    name="position"
                    value={filters.position || ""}
                    onChange={handleChange}
                    placeholder="Position ID"
                    className="w-full border border-gray-300 dark:border-gray-600 rounded px-3 py-2 text-sm bg-white dark:bg-gzc-mid-black text-gray-900 dark:text-white"
                />
            </div>
        </div>
    );
};

export default PortfolioFilters;
