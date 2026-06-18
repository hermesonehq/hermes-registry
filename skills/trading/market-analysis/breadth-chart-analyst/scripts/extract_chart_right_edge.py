#!/usr/bin/env python3
"""
Chart Right Edge Extractor

Extracts the rightmost portion of chart images to help LLM focus on
the latest data points and avoid misreading historical data.

Usage:
    python extract_chart_right_edge.py <image_path> [--percent 25] [--output <output_path>]

Examples:
    # Extract right 25% (default)
    python extract_chart_right_edge.py charts/2025-12-22/IMG_5499.jpeg

    # Extract right 30%
    python extract_chart_right_edge.py charts/2025-12-22/IMG_5499.jpeg --percent 30

    # Specify output path
    python extract_chart_right_edge.py charts/2025-12-22/IMG_5499.jpeg --output /tmp/right_edge.jpeg
"""

import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont


def extract_right_edge(image_path: str, right_percentage: int = 25, output_path: str = None) -> str:
    """
    Extract the rightmost portion of a chart image.

    Args:
        image_path: Path to the source chart image
        right_percentage: Percentage of the image width to extract from the right (default: 25%)
        output_path: Optional output path. If not specified, saves to same directory with '_right_edge' suffix

    Returns:
        Path to the extracted image
    """
    # Open the image
    img = Image.open(image_path)
    width, height = img.size

    # Calculate crop boundaries
    left = int(width * (1 - right_percentage / 100))

    # Crop the right portion
    right_edge = img.crop((left, 0, width, height))

    # Determine output path
    if output_path is None:
        base, ext = os.path.splitext(image_path)
        output_path = f"{base}_right_edge{ext}"

    # Save the cropped image
    right_edge.save(output_path, quality=95)

    return output_path


def extract_right_edge_with_marker(
    image_path: str, right_percentage: int = 25, output_path: str = None
) -> str:
    """
    Extract the rightmost portion and add a visual marker showing the analysis region.
    Also creates a full image with the analysis region highlighted.

    Args:
        image_path: Path to the source chart image
        right_percentage: Percentage of the image width to extract from the right (default: 25%)
        output_path: Optional output path for the cropped image

    Returns:
        Tuple of (cropped_image_path, marked_full_image_path)
    """
    # Open the image
    img = Image.open(image_path)
    width, height = img.size

    # Calculate crop boundaries
    left = int(width * (1 - right_percentage / 100))

    # Create a copy for marking
    marked_img = img.copy()
    draw = ImageDraw.Draw(marked_img)

    # Draw a semi-transparent overlay on the left (non-analysis) portion
    # We'll draw vertical lines to indicate the analysis boundary
    line_color = (255, 0, 0)  # Red
    line_width = 3

    # Draw vertical line at the boundary
    draw.line([(left, 0), (left, height)], fill=line_color, width=line_width)

    # Add text label
    try:
        # Try to use a default font
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
    except Exception:
        font = ImageFont.load_default()

    label = f"← Analysis Region ({right_percentage}%)"
    draw.text((left + 10, 10), label, fill=line_color, font=font)

    # Save marked full image
    base, ext = os.path.splitext(image_path)
    marked_output_path = f"{base}_marked{ext}"
    marked_img.save(marked_output_path, quality=95)

    # Crop and save the right portion
    right_edge = img.crop((left, 0, width, height))

    if output_path is None:
        output_path = f"{base}_right_edge{ext}"

    right_edge.save(output_path, quality=95)

    return output_path, marked_output_path


def process_breadth_charts(charts_dir: str, right_percentage: int = 25) -> dict:
    """
    Process all breadth-related charts in a directory.

    Looks for charts with 'breadth', 'uptrend', or '200ma' in the filename (case-insensitive).

    Args:
        charts_dir: Directory containing chart images
        right_percentage: Percentage to extract from right

    Returns:
        Dictionary mapping original paths to extracted paths
    """
    results = {}

    # Supported image extensions
    extensions = {".jpeg", ".jpg", ".png", ".gif", ".webp"}

    # Keywords to identify breadth charts
    breadth_keywords = ["breadth", "uptrend", "200ma", "200-day", "sp500_breadth", "s&p_breadth"]

    for filename in os.listdir(charts_dir):
        # Check if it's an image file
        _, ext = os.path.splitext(filename)
        if ext.lower() not in extensions:
            continue

        # Check if it's likely a breadth chart (by filename)
        # Note: This is a heuristic; the skill can also process explicitly specified files
        filename_lower = filename.lower()
        is_breadth_chart = any(keyword in filename_lower for keyword in breadth_keywords)

        if is_breadth_chart or True:  # Process all images for now
            image_path = os.path.join(charts_dir, filename)

            # Skip already processed files
            if "_right_edge" in filename or "_marked" in filename:
                continue

            try:
                output_path = extract_right_edge(image_path, right_percentage)
                results[image_path] = output_path
                print(f"✓ Processed: {filename} → {os.path.basename(output_path)}")
            except Exception as e:
                print(f"✗ Error processing {filename}: {str(e)}", file=sys.stderr)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Extract the rightmost portion of chart images for focused analysis.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract right 25% of a single image
  python extract_chart_right_edge.py charts/2025-12-22/IMG_5499.jpeg

  # Extract right 30% with custom output path
  python extract_chart_right_edge.py charts/2025-12-22/IMG_5499.jpeg --percent 30 --output /tmp/breadth_right.jpeg

  # Process all images in a directory
  python extract_chart_right_edge.py --dir charts/2025-12-22/ --percent 25

  # Create marked version showing analysis region
  python extract_chart_right_edge.py charts/2025-12-22/IMG_5499.jpeg --mark
        """,
    )

    parser.add_argument("image_path", nargs="?", help="Path to the chart image")
    parser.add_argument(
        "--percent",
        type=int,
        default=25,
        help="Percentage of width to extract from right (default: 25)",
    )
    parser.add_argument("--output", "-o", help="Output path for the extracted image")
    parser.add_argument("--dir", "-d", help="Process all images in a directory")
    parser.add_argument(
        "--mark",
        action="store_true",
        help="Also create a marked version showing the analysis region",
    )

    args = parser.parse_args()

    # Directory mode
    if args.dir:
        if not os.path.isdir(args.dir):
            print(f"Error: Directory not found: {args.dir}", file=sys.stderr)
            sys.exit(1)

        print(f"Processing charts in: {args.dir}")
        print(f"Extracting right {args.percent}% of each image")
        print()

        results = process_breadth_charts(args.dir, args.percent)

        print()
        print(f"Processed {len(results)} images")
        return

    # Single image mode
    if not args.image_path:
        parser.print_help()
        sys.exit(1)

    if not os.path.isfile(args.image_path):
        print(f"Error: File not found: {args.image_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Processing: {args.image_path}")
    print(f"Extracting right {args.percent}%")

    if args.mark:
        cropped_path, marked_path = extract_right_edge_with_marker(
            args.image_path, args.percent, args.output
        )
        print(f"✓ Cropped image saved to: {cropped_path}")
        print(f"✓ Marked image saved to: {marked_path}")
    else:
        output_path = extract_right_edge(args.image_path, args.percent, args.output)
        print(f"✓ Saved to: {output_path}")


if __name__ == "__main__":
    main()
