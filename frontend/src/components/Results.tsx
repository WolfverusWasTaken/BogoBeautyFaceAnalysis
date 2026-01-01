import type { ParsedResult, Product } from "../api";

interface ResultsProps {
    result: ParsedResult;
}

const skinToneColors: Record<string, string> = {
    fair: "#fce4d6",
    light: "#f5d5c8",
    medium: "#d4a574",
    dark: "#8d5524",
};

const hairColors: Record<string, string> = {
    black: "#0a0a0a",
    "dark brown": "#2c1810",
    brown: "#4a2c17",
    "light brown": "#8b4513",
    blonde: "#e8d5b7",
    red: "#8b2500",
    gray: "#808080",
    dark: "#1a1a1a",
};

const eyebrowColors: Record<string, string> = {
    black: "#0a0a0a",
    "dark brown": "#2c1810",
    brown: "#4a2c17",
    blonde: "#c4a35a",
    gray: "#808080",
    dark: "#1a1a1a",
};

function ColorSwatch({
    color,
    label,
    hexColor,
}: {
    color: string;
    label: string;
    hexColor: string;
}) {
    return (
        <div className="flex items-center gap-2">
            <div
                className="w-7 h-7 sm:w-8 sm:h-8 rounded-full border-2 border-white/20 shadow-md shrink-0"
                style={{ backgroundColor: hexColor }}
            />
            <div className="min-w-0">
                <div className="text-[9px] sm:text-[10px] text-[var(--muted)] uppercase tracking-wide">{label}</div>
                <div className="text-xs sm:text-sm font-medium capitalize truncate">{color}</div>
            </div>
        </div>
    );
}

function ProductCard({ product }: { product: Product }) {
    return (
        <div className="glass-card p-2 transition-all-smooth hover:scale-[1.02] hover:border-[var(--accent)]">
            <div className="min-w-0">
                <div className="text-[9px] sm:text-[10px] text-[var(--accent)] font-semibold uppercase tracking-wide truncate">
                    {product["Brand Name"]}
                </div>
                <div className="text-[11px] sm:text-xs font-medium truncate">{product["Product Name"]}</div>
                <div className="flex items-center gap-2 mt-1 text-[11px] sm:text-xs">
                    <span className="text-[var(--accent-coral)] font-semibold">
                        ${product.Price?.toFixed(2) || "N/A"}
                    </span>
                    <span className="flex items-center gap-0.5 text-[var(--muted)]">
                        <span className="text-yellow-400">★</span>
                        {product.Ratings?.toFixed(1) || "N/A"}
                    </span>
                </div>
            </div>
        </div>
    );
}

export function Results({ result }: ResultsProps) {
    return (
        <div className="space-y-3 text-sm">
            {/* Detected Features */}
            <div>
                <h3 className="text-xs sm:text-sm font-semibold mb-2">Detected Features</h3>
                <div className="grid grid-cols-3 gap-1 sm:gap-2">
                    <ColorSwatch
                        color={result.skin_tone}
                        label="Skin"
                        hexColor={skinToneColors[result.skin_tone] || "#c9a677"}
                    />
                    <ColorSwatch
                        color={result.hair_color}
                        label="Hair"
                        hexColor={hairColors[result.hair_color] || "#4a2c17"}
                    />
                    <ColorSwatch
                        color={result.eyebrow_color}
                        label="Brow"
                        hexColor={eyebrowColors[result.eyebrow_color] || "#3b2314"}
                    />
                </div>
            </div>

            {/* Foundation Recommendations */}
            {result.foundations.length > 0 && (
                <div>
                    <h3 className="text-xs sm:text-sm font-semibold mb-2">Foundations</h3>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                        {result.foundations.map((product, idx) => (
                            <ProductCard key={idx} product={product} />
                        ))}
                    </div>
                </div>
            )}

            {/* Lipstick Recommendations */}
            {result.lipsticks.length > 0 && (
                <div>
                    <h3 className="text-xs sm:text-sm font-semibold mb-2">Lipsticks</h3>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                        {result.lipsticks.map((product, idx) => (
                            <ProductCard key={idx} product={product} />
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
