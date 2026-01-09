#!/bin/bash

# Download all pages from Dutton Cavanaugh website

BASE_URL="https://www.duttoncavanaugh.com"
OUTPUT_DIR="./public"

# User agent string
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Pages to download
pages=(
    "/contact:contact.html"
    "/griffin_accounting/about:griffin_accounting-about.html"
    "/griffin/bookkeeping:griffin-bookkeeping.html"
    "/griffin/business-services:griffin-business-services.html"
    "/griffin/tax-planning:griffin-tax-planning.html"
    "/griffin/taxes:griffin-taxes.html"
    "/News:News.html"
    "/practiceareas:practiceareas.html"
    "/services:services.html"
)

echo "========================================"
echo "Downloading Dutton Cavanaugh Pages"
echo "========================================"
echo ""

count=0
total=${#pages[@]}

for page in "${pages[@]}"; do
    ((count++))

    # Split path and filename
    path="${page%%:*}"
    filename="${page##*:}"

    url="${BASE_URL}${path}"
    output_file="${OUTPUT_DIR}/${filename}"

    echo "[$count/$total] Downloading: $url"
    echo "           → $output_file"

    curl -s -A "$UA" \
        -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
        -H "Accept-Language: en-US,en;q=0.5" \
        "$url" > "$output_file"

    if [ $? -eq 0 ] && [ -s "$output_file" ]; then
        # Check if it's not a 403 error page
        if grep -q "403 Forbidden" "$output_file"; then
            echo "           ✗ Access Forbidden (403)"
        else
            echo "           ✓ Success"
        fi
    else
        echo "           ✗ Failed"
    fi

    echo ""

    # Be polite - add delay between requests
    sleep 1
done

echo "========================================"
echo "Download Complete!"
echo "========================================"
echo "Total pages downloaded: $count"
echo ""
echo "Start the server with: npm start"
echo "Then visit: http://localhost:3000"
