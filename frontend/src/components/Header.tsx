interface HeaderProps {
    logoSrc: string;
}

export function Header({ logoSrc }: HeaderProps) {
    return (
        <header className="glass-card mx-4 mt-3 mb-3">
            <div className="flex items-center gap-3 p-3">
                {/* Logo */}
                <img
                    src={logoSrc}
                    alt="BogoBeauty Logo"
                    className="w-10 h-10 sm:w-12 sm:h-12 rounded-full object-cover border border-[var(--border)] shadow-lg bg-white shrink-0"
                />

                {/* Title & Description */}
                <div className="flex-1 min-w-0">
                    <h1 className="text-lg sm:text-xl font-bold tracking-tight">
                        <span className="bg-gradient-to-r from-[var(--accent)] via-[var(--accent-pink)] to-[var(--accent-coral)] bg-clip-text text-transparent">
                            BogoBeauty
                        </span>{" "}
                        <span className="hidden xs:inline">Face Analyzer</span>
                    </h1>
                    <p className="text-[var(--muted)] text-xs truncate hidden sm:block">
                        AI-powered facial analysis for personalized beauty recommendations
                    </p>
                </div>

                {/* Feature tags - hidden on mobile */}
                <div className="hidden lg:flex gap-2 shrink-0">
                    {["Color Analysis", "Product Matching", "AI Powered"].map((tag) => (
                        <span
                            key={tag}
                            className="px-2 py-0.5 rounded-full text-xs font-medium bg-[var(--border)] text-[var(--muted)]"
                        >
                            {tag}
                        </span>
                    ))}
                </div>
            </div>

            {/* Decorative gradient line */}
            <div className="h-0.5 bg-gradient-to-r from-[var(--accent)] via-[var(--accent-pink)] to-[var(--accent-coral)]" />
        </header>
    );
}
