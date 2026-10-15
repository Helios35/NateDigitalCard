#!/usr/bin/env bash
# Static audit of the card: the greps behind checks 1-4, 9 and 10 of Unit 03.
# usage: bash audit.sh <projectDir>
# Every command below is printed before its output, so the notes can quote it verbatim.
cd "$1" || exit 1
F=index.html
run() { echo; echo "\$ $*"; eval "$@"; echo "[exit $?]"; }

# Line ranges: the <style> element, the :root token block inside it, and the END EDIT marker.
S0=$(grep -n '^<style>' $F | cut -d: -f1); S1=$(grep -n '^</style>' $F | cut -d: -f1)
T0=$(grep -n '^  :root {' $F | cut -d: -f1); T1=$(awk -v s="$T0" 'NR>s && /^  }$/ {print NR; exit}' $F)
E=$(grep -n 'END EDIT' $F | cut -d: -f1)
echo "style lines $S0-$S1; token block (:root) lines $T0-$T1; END EDIT at line $E"
# Everything in index.html except the token block, comments kept (a literal in a comment still counts).
OUTSIDE="awk -v a=$T0 -v b=$T1 'NR<a || NR>b {print NR\": \"\$0}' $F"

echo; echo "################ CHECK 1: one token block ################"
run "grep -c '^  :root {' $F"
run "awk -v a=$T0 -v b=$T1 'NR>=a && NR<=b' $F | grep -oE '^ *--[a-z0-9-]+' | sort | uniq -d"
run "awk 'NR>=$S0 && NR<=$S1' $F | grep -nE '^\s*--[a-z0-9-]+:' | awk -F: -v a=$T0 -v s=$S0 -v b=$T1 '{ln=\$1+s-1; if (ln<a || ln>b) print ln\": \"\$0}'"
echo "# transition / animation times written outside the block (0s = an instant swap is allowed):"
run "$OUTSIDE | awk -v s=$S0 -v e=$S1 -F': ' '\$1>=s && \$1<=e' | grep -E 'transition|animation' | grep -oE '[0-9]*\.?[0-9]+m?s\b' | sort | uniq -c"
run "$OUTSIDE | awk -v s=$S0 -v e=$S1 -F': ' '\$1>=s && \$1<=e' | grep -nE '(transition|animation)[^;]*[^0-9](\.[0-9]+|[1-9][0-9]*)m?s\b'"
echo "# easing curves outside the block:"
run "$OUTSIDE | grep -E 'cubic-bezier'"
echo "# font families, sizes, radii, shadows written as literals outside the block:"
run "$OUTSIDE | awk -v s=$S0 -v e=$S1 -F': ' '\$1>=s && \$1<=e' | grep -E 'font-family:' | grep -v 'var(--'"
run "$OUTSIDE | awk -v s=$S0 -v e=$S1 -F': ' '\$1>=s && \$1<=e' | grep -oE 'font-size: *[^;]+' | sort | uniq -c"
run "$OUTSIDE | awk -v s=$S0 -v e=$S1 -F': ' '\$1>=s && \$1<=e' | grep -E 'border-radius:' | grep -v 'border-radius: *var(--'"
run "$OUTSIDE | awk -v s=$S0 -v e=$S1 -F': ' '\$1>=s && \$1<=e' | grep -E '(box|text)-shadow:'"

echo; echo "################ CHECK 2: no loose colour values ################"
echo "# hex anywhere outside the token block (the grain is base64; decoded separately below):"
run "$OUTSIDE | grep -nE '#[0-9a-fA-F]{3,8}\b' | grep -vE 'href=\"#|getElementById|url\(#|#(qr|share|flip|save|links|video|poster|eyebrow|name|back|front|hero|content|toast|quick|badges|role|foot|tap)'"
echo "# rgb()/rgba()/hsl() outside the token block:"
run "$OUTSIDE | grep -nE '(rgba?|hsla?|hwb|lab|lch|oklab|oklch|color-mix)\('"
echo "# CSS named colours used as values outside the block (comments stripped; transparent/currentColor are keywords, listed separately):"
run "python -I \"$(dirname "$0")/named_colours.py\" $F $T0 $T1"
echo "# theme-color and every inline style= attribute:"
run "grep -n 'theme-color' $F"
run "grep -nE ' style=\"' $F"
echo "# colour literals in the script (QR fill, inline styles set from JS):"
run "awk '/^<script>\$/,/^<\/script>\$/' $F | grep -nE '#[0-9a-fA-F]{6}\b|rgba?\(|\.style\.(color|background|fill|stroke)|fill=\"#'"
echo "# the grain texture, decoded:"
run "grep -oE 'base64,[A-Za-z0-9+/=]+' $F | cut -d, -f2 | base64 -d; echo"
echo "# every SVG file that deploys:"
run "grep -oiE '#[0-9a-f]{3,8}\b|rgba?\([^)]*\)' brand/*.svg | sort | uniq -c"

echo; echo "################ CHECK 3: no old tokens, fonts or logos ################"
run "grep -nE -- '--(gold|gold-deep|cream|black|surface|line|line-soft)\b' $F brand/*.svg"
run "grep -rniE 'space.?grotesk' --include='*' . --exclude-dir=.git --exclude-dir=.claude --exclude-dir=Unit02_verification --exclude=Unit0*_BUILD_NOTES.md"
run "grep -rnE 'logo-cream|logo-dark|mark-cream' . --exclude-dir=.git --exclude-dir=.claude --exclude-dir=Unit02_verification --exclude=Unit0*_BUILD_NOTES.md"
run "ls fonts brand"

echo; echo "################ CHECK 4: fin's scales only ################"
run "grep -nE -- '--radius[a-z-]*:' $F"
run "grep -noE 'border-radius: *[^;]+' $F | sort -t: -k3 | uniq -c -f0"
run "grep -nE -- '--shadow-[a-z0-9]+:' $F"
run "grep -noE 'box-shadow: *[^;]+' $F"
run "grep -noE 'font-family: *[^;]+' $F"
run "grep -oE 'font-size: *[^;]+' $F | sort | uniq -c"
run "grep -oE 'font-weight: *[^;]+' $F | sort | uniq -c"

echo; echo "################ CHECK 9: content lives in the edit block ################"
echo "# quoted words in the markup and script below END EDIT (line $E):"
run "awk -v e=$E 'NR>e' $F | grep -nE 'aria-label=\"[^\"]+\"|alt=\"[^\"]+\"|title=\"[^\"]+\"|placeholder=' | sed 's/^/+$E /'"
run "awk -v e=$E 'NR>e' $F | grep -nE '\"[A-Z][a-z]+( [a-z]+)+\"|\" to [a-z]+|en-US|lang=' | sed 's/^/+$E /'"
run "awk -v e=$E 'NR>e' $F | grep -nE '>[^<{}]*[A-Za-z]{3,}[^<{}]*<' | grep -v '<script\\|<style\\|//' | sed 's/^/+$E /'"

echo; echo "################ CHECK 10: nothing dead ################"
echo "# classes defined in CSS but never used in markup or script:"
run "python -I \"$(dirname "$0")/dead.py\" $F"
echo "# files that deploy (tracked, minus .vercelignore) that the page never references (licences are expected):"
run "comm -23 <(git ls-files | sort) <(git ls-files -ci --exclude-from=.vercelignore | sort) | grep -vE '^\.(gitignore|vercelignore)\$' | while read f; do b=\$(basename \"\$f\"); [ \"\$f\" = $F ] || grep -qF \"\$b\" $F || echo \"deploys, unreferenced: \$f\"; done"
run "cat .vercelignore"
