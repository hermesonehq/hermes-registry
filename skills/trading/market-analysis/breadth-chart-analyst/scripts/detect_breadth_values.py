#!/usr/bin/env python3
"""
Breadth Chart Value Detector (OpenCV Version)

Automatically detects the 200-Day MA and 8-Day MA values from S&P 500 Breadth Index charts
using OpenCV image processing for high-accuracy detection.

This script analyzes chart images to:
1. Calibrate Y-axis using reference lines (0.73 red dashed, 0.23 blue dashed)
2. Detect green line (200-Day MA) position at the right edge
3. Detect orange line (8-Day MA) position at the right edge
4. Convert pixel positions to percentage values

Requirements:
    pip install opencv-python numpy

Usage:
    python detect_breadth_values.py <image_path>
    python detect_breadth_values.py charts/2025-12-22/IMG_5499.jpeg
    python detect_breadth_values.py charts/2025-12-22/IMG_5499.jpeg --debug

Output:
    JSON with detected values:
    {
        "200ma": 0.60,
        "8ma": 0.63,
        "confidence": "high"
    }
"""

import argparse
import json
import os
import sys
from typing import Any, Optional

import cv2
import numpy as np


class BreadthChartDetector:
    """
    Detects 200-Day MA and 8-Day MA values from S&P 500 Breadth Index charts.

    The chart has:
    - Green line: 200-Day Moving Average of stocks above their 200-Day MA
    - Orange line: 8-Day Moving Average (short-term indicator)
    - Red dashed line: Upper reference at 0.73 (73%)
    - Blue dashed line: Lower reference at 0.23 (23%)
    - Pink background: Indicates downtrend periods
    """

    # Reference values for Y-axis calibration
    RED_LINE_VALUE = 0.73  # Upper reference line
    BLUE_LINE_VALUE = 0.23  # Lower reference line

    # HSV color ranges for OpenCV (H: 0-179, S: 0-255, V: 0-255)
    # OpenCV uses H/2 (0-179 instead of 0-360)

    # Green line (200MA): Hue ~60-80 in OpenCV scale
    GREEN_HSV_LOW = np.array([35, 60, 60])
    GREEN_HSV_HIGH = np.array([85, 255, 255])

    # Orange line (8MA): Hue ~10-25 in OpenCV scale
    ORANGE_HSV_LOW = np.array([5, 100, 100])
    ORANGE_HSV_HIGH = np.array([25, 255, 255])

    # Red reference line: Hue ~0-10 or 170-179
    RED_HSV_LOW1 = np.array([0, 80, 80])
    RED_HSV_HIGH1 = np.array([10, 255, 255])
    RED_HSV_LOW2 = np.array([170, 80, 80])
    RED_HSV_HIGH2 = np.array([179, 255, 255])

    # Blue reference line: Hue ~100-130
    BLUE_HSV_LOW = np.array([95, 60, 60])
    BLUE_HSV_HIGH = np.array([135, 255, 255])

    def __init__(self, image_path: str, debug: bool = False):
        """
        Initialize the detector with an image path.

        Args:
            image_path: Path to the breadth chart image
            debug: If True, saves debug images showing detection results
        """
        self.image_path = image_path
        self.debug = debug

        # Read image with OpenCV (BGR format)
        self.img_bgr = cv2.imread(image_path)
        if self.img_bgr is None:
            raise ValueError(f"Could not read image: {image_path}")

        self.height, self.width = self.img_bgr.shape[:2]

        # Convert to HSV for color detection
        self.img_hsv = cv2.cvtColor(self.img_bgr, cv2.COLOR_BGR2HSV)

        # Calibration results
        self.red_line_y: Optional[int] = None
        self.blue_line_y: Optional[int] = None
        self.y_scale: Optional[float] = None
        self.y_offset: Optional[float] = None

        # Debug info
        self.debug_info: dict[str, Any] = {}

    def _create_color_mask(
        self,
        hsv_low: np.ndarray,
        hsv_high: np.ndarray,
        hsv_low2: np.ndarray = None,
        hsv_high2: np.ndarray = None,
    ) -> np.ndarray:
        """
        Create a binary mask for pixels within the specified HSV range.

        Args:
            hsv_low: Lower HSV bounds
            hsv_high: Upper HSV bounds
            hsv_low2: Optional second lower bounds (for wraparound colors like red)
            hsv_high2: Optional second upper bounds

        Returns:
            Binary mask (255 where color matches, 0 elsewhere)
        """
        mask = cv2.inRange(self.img_hsv, hsv_low, hsv_high)

        if hsv_low2 is not None and hsv_high2 is not None:
            mask2 = cv2.inRange(self.img_hsv, hsv_low2, hsv_high2)
            mask = cv2.bitwise_or(mask, mask2)

        return mask

    def _find_horizontal_line_y(
        self, mask: np.ndarray, min_width_ratio: float = 0.15
    ) -> Optional[int]:
        """
        Find the Y coordinate of a horizontal line in the mask.

        Uses horizontal projection (sum of pixels per row) to find lines.

        Args:
            mask: Binary mask of the target color
            min_width_ratio: Minimum ratio of image width the line should span

        Returns:
            Y coordinate of the detected line, or None
        """
        min_width = int(self.width * min_width_ratio)

        # Calculate horizontal projection (sum of white pixels per row)
        h_projection = np.sum(mask > 0, axis=1)

        # Find rows with significant horizontal extent
        candidate_rows = np.where(h_projection >= min_width)[0]

        if len(candidate_rows) == 0:
            return None

        # Group consecutive rows and find the strongest group
        # (handles thick lines)
        groups = []
        current_group = [candidate_rows[0]]

        for i in range(1, len(candidate_rows)):
            if candidate_rows[i] - candidate_rows[i - 1] <= 3:  # Allow 3px gaps
                current_group.append(candidate_rows[i])
            else:
                groups.append(current_group)
                current_group = [candidate_rows[i]]
        groups.append(current_group)

        # Find the group with the maximum total projection value
        best_group = max(groups, key=lambda g: sum(h_projection[y] for y in g))

        # Return the center of the best group
        return int(np.mean(best_group))

    def _detect_reference_lines(self) -> tuple[bool, bool]:
        """
        Detect the red (0.73) and blue (0.23) reference lines for Y-axis calibration.

        Returns:
            Tuple of (red_detected, blue_detected)
        """
        # Create masks for reference lines
        red_mask = self._create_color_mask(
            self.RED_HSV_LOW1, self.RED_HSV_HIGH1, self.RED_HSV_LOW2, self.RED_HSV_HIGH2
        )
        blue_mask = self._create_color_mask(self.BLUE_HSV_LOW, self.BLUE_HSV_HIGH)

        if self.debug:
            self.debug_info["red_mask"] = red_mask
            self.debug_info["blue_mask"] = blue_mask

        # Find line positions
        self.red_line_y = self._find_horizontal_line_y(red_mask)
        self.blue_line_y = self._find_horizontal_line_y(blue_mask)

        return (self.red_line_y is not None, self.blue_line_y is not None)

    def _calibrate_y_axis(self) -> bool:
        """
        Calibrate Y-axis using detected reference lines.

        The Y-axis is inverted in images (0 at top), so:
        - Red line (0.73) should be at lower Y pixel value (higher in image)
        - Blue line (0.23) should be at higher Y pixel value (lower in image)

        Returns:
            True if calibration succeeded, False otherwise
        """
        red_detected, blue_detected = self._detect_reference_lines()

        if not red_detected or not blue_detected:
            # Fallback: estimate based on image dimensions
            print("Warning: Could not detect reference lines. Using estimated calibration.")
            chart_top = int(self.height * 0.1)
            chart_bottom = int(self.height * 0.85)

            # Estimate reference line positions
            if not red_detected:
                self.red_line_y = chart_top + int((chart_bottom - chart_top) * (1 - 0.73))
            if not blue_detected:
                self.blue_line_y = chart_top + int((chart_bottom - chart_top) * (1 - 0.23))

        # Ensure red line is above blue line (lower Y value = higher position)
        if self.red_line_y > self.blue_line_y:
            self.red_line_y, self.blue_line_y = self.blue_line_y, self.red_line_y

        # Calculate linear transformation: value = scale * pixel_y + offset
        pixel_diff = self.blue_line_y - self.red_line_y
        value_diff = self.BLUE_LINE_VALUE - self.RED_LINE_VALUE  # Negative (0.23 - 0.73)

        if pixel_diff == 0:
            return False

        self.y_scale = value_diff / pixel_diff
        self.y_offset = self.RED_LINE_VALUE - (self.y_scale * self.red_line_y)

        return True

    def _pixel_y_to_value(self, pixel_y: int) -> float:
        """Convert pixel Y coordinate to percentage value (0-1)."""
        if self.y_scale is None or self.y_offset is None:
            raise ValueError("Y-axis not calibrated. Call _calibrate_y_axis first.")
        return self.y_scale * pixel_y + self.y_offset

    def _detect_line_at_right_edge(
        self, mask: np.ndarray, right_percent: float = 0.15, line_name: str = "line"
    ) -> Optional[float]:
        """
        Detect a colored line's Y position at the right edge of the chart.

        Uses weighted centroid calculation for sub-pixel accuracy.

        Args:
            mask: Binary mask of the target line color
            right_percent: Percentage of image width to analyze from right edge
            line_name: Name for debug logging

        Returns:
            Detected value (0-1), or None if not detected
        """
        right_start = int(self.width * (1 - right_percent))

        # Extract the right edge region
        right_region = mask[:, right_start:]

        # Find all white (line) pixels in the region
        y_coords, x_coords = np.where(right_region > 0)

        if len(y_coords) == 0:
            return None

        # Weight by x position (prefer rightmost pixels for current value)
        # Pixels closer to right edge (higher x) get more weight
        weights = (x_coords - x_coords.min() + 1).astype(float)
        weights = weights**2  # Quadratic weighting for more emphasis on rightmost

        # Calculate weighted Y centroid
        weighted_y = np.average(y_coords, weights=weights)

        # Also calculate the mode (most common Y) for validation
        y_bins = np.bincount(y_coords, minlength=self.height)
        mode_y = np.argmax(y_bins)

        # Use weighted average if it's reasonably close to mode
        if abs(weighted_y - mode_y) > 20:
            # Large discrepancy - use mode for robustness
            final_y = mode_y
        else:
            final_y = weighted_y

        if self.debug:
            self.debug_info[f"{line_name}_weighted_y"] = weighted_y
            self.debug_info[f"{line_name}_mode_y"] = mode_y
            self.debug_info[f"{line_name}_final_y"] = final_y
            self.debug_info[f"{line_name}_pixel_count"] = len(y_coords)

        # Convert to actual value
        value = self._pixel_y_to_value(int(final_y))

        # Clamp to reasonable range
        value = max(0.0, min(1.0, value))

        return round(value, 3)

    def _detect_green_line(self) -> Optional[float]:
        """Detect the 200-Day MA (green) line value."""
        green_mask = self._create_color_mask(self.GREEN_HSV_LOW, self.GREEN_HSV_HIGH)

        if self.debug:
            self.debug_info["green_mask"] = green_mask

        return self._detect_line_at_right_edge(green_mask, line_name="green")

    def _detect_orange_line(self) -> Optional[float]:
        """Detect the 8-Day MA (orange) line value."""
        orange_mask = self._create_color_mask(self.ORANGE_HSV_LOW, self.ORANGE_HSV_HIGH)

        if self.debug:
            self.debug_info["orange_mask"] = orange_mask

        return self._detect_line_at_right_edge(orange_mask, line_name="orange")

    def _assess_confidence(self, value_200ma: Optional[float], value_8ma: Optional[float]) -> str:
        """
        Assess confidence level of the detection.

        Returns:
            'high', 'medium', or 'low'
        """
        if value_200ma is None and value_8ma is None:
            return "failed"

        # Check if reference lines were detected (not estimated)
        red_detected, blue_detected = (
            (
                self.debug_info.get("red_mask") is not None
                and self._find_horizontal_line_y(
                    self.debug_info.get("red_mask", np.zeros((1, 1), dtype=np.uint8))
                )
                is not None,
                self.debug_info.get("blue_mask") is not None
                and self._find_horizontal_line_y(
                    self.debug_info.get("blue_mask", np.zeros((1, 1), dtype=np.uint8))
                )
                is not None,
            )
            if self.debug
            else (self.red_line_y is not None, self.blue_line_y is not None)
        )

        if not (red_detected and blue_detected):
            base_confidence = "low"
        else:
            base_confidence = "high"

        # Degrade confidence if only one value detected
        if value_200ma is None or value_8ma is None:
            if base_confidence == "high":
                return "medium"
            return "low"

        # Check for reasonable value range
        if not (0.1 <= value_200ma <= 0.9) or not (0.1 <= value_8ma <= 0.9):
            return "low"

        # Check pixel counts if available
        if self.debug:
            green_count = self.debug_info.get("green_pixel_count", 0)
            orange_count = self.debug_info.get("orange_pixel_count", 0)
            if green_count < 20 or orange_count < 20:
                if base_confidence == "high":
                    return "medium"

        return base_confidence

    def analyze(self) -> dict[str, Any]:
        """
        Perform full analysis of the breadth chart.

        Returns:
            Dictionary with detected values and metadata
        """
        # Calibrate Y-axis
        calibrated = self._calibrate_y_axis()

        # Detect line values
        value_200ma = self._detect_green_line()
        value_8ma = self._detect_orange_line()

        # Assess confidence
        confidence = self._assess_confidence(value_200ma, value_8ma)

        # Build result
        result = {
            "200ma": value_200ma,
            "200ma_percent": f"{value_200ma * 100:.1f}%" if value_200ma else None,
            "8ma": value_8ma,
            "8ma_percent": f"{value_8ma * 100:.1f}%" if value_8ma else None,
            "confidence": confidence,
            "calibration": {
                "red_line_y": self.red_line_y,
                "blue_line_y": self.blue_line_y,
                "calibrated": calibrated,
                "y_scale": self.y_scale,
                "y_offset": self.y_offset,
            },
            "image": {"path": self.image_path, "width": self.width, "height": self.height},
        }

        # Add interpretation
        if value_200ma is not None:
            if value_200ma >= 0.60:
                result["200ma_interpretation"] = "healthy (>=60%)"
            elif value_200ma >= 0.50:
                result["200ma_interpretation"] = "narrow_rally (50-60%)"
            elif value_200ma >= 0.40:
                result["200ma_interpretation"] = "caution (40-50%)"
            else:
                result["200ma_interpretation"] = "weak (<40%)"

        if value_8ma is not None:
            if value_8ma >= 0.73:
                result["8ma_interpretation"] = "overbought (>=73%)"
            elif value_8ma >= 0.60:
                result["8ma_interpretation"] = "healthy_bullish (60-73%)"
            elif value_8ma >= 0.40:
                result["8ma_interpretation"] = "neutral (40-60%)"
            elif value_8ma >= 0.23:
                result["8ma_interpretation"] = "weak (23-40%)"
            else:
                result["8ma_interpretation"] = "oversold (<23%)"

        if self.debug:
            result["debug"] = {
                "green_pixel_count": self.debug_info.get("green_pixel_count"),
                "orange_pixel_count": self.debug_info.get("orange_pixel_count"),
                "green_weighted_y": self.debug_info.get("green_weighted_y"),
                "orange_weighted_y": self.debug_info.get("orange_weighted_y"),
            }
            self._save_debug_image(value_200ma, value_8ma)

        return result

    def _save_debug_image(self, value_200ma: Optional[float], value_8ma: Optional[float]):
        """Save a debug image with detected values marked."""
        debug_img = self.img_bgr.copy()

        # Draw reference lines
        if self.red_line_y:
            cv2.line(
                debug_img, (0, self.red_line_y), (self.width, self.red_line_y), (0, 0, 255), 2
            )  # Red in BGR
            cv2.putText(
                debug_img,
                f"0.73 ref (y={self.red_line_y})",
                (10, self.red_line_y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                1,
            )

        if self.blue_line_y:
            cv2.line(
                debug_img, (0, self.blue_line_y), (self.width, self.blue_line_y), (255, 0, 0), 2
            )  # Blue in BGR
            cv2.putText(
                debug_img,
                f"0.23 ref (y={self.blue_line_y})",
                (10, self.blue_line_y + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 0, 0),
                1,
            )

        # Mark detected values on right edge
        right_x = self.width - 200

        if value_200ma is not None and self.y_scale is not None:
            y_200ma = int((value_200ma - self.y_offset) / self.y_scale)
            cv2.circle(debug_img, (right_x, y_200ma), 15, (0, 255, 0), 3)  # Green
            cv2.putText(
                debug_img,
                f"200MA: {value_200ma:.3f} ({value_200ma * 100:.1f}%)",
                (right_x - 180, y_200ma - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        if value_8ma is not None and self.y_scale is not None:
            y_8ma = int((value_8ma - self.y_offset) / self.y_scale)
            cv2.circle(debug_img, (right_x + 40, y_8ma), 15, (0, 165, 255), 3)  # Orange in BGR
            cv2.putText(
                debug_img,
                f"8MA: {value_8ma:.3f} ({value_8ma * 100:.1f}%)",
                (right_x - 180, y_8ma + 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 165, 255),
                2,
            )

        # Save color masks as well
        base, ext = os.path.splitext(self.image_path)
        debug_path = f"{base}_debug_detection{ext}"
        cv2.imwrite(debug_path, debug_img)
        print(f"Debug detection image saved to: {debug_path}")

        # Save individual masks if available
        if "green_mask" in self.debug_info:
            mask_path = f"{base}_debug_green_mask.png"
            cv2.imwrite(mask_path, self.debug_info["green_mask"])
            print(f"Green mask saved to: {mask_path}")

        if "orange_mask" in self.debug_info:
            mask_path = f"{base}_debug_orange_mask.png"
            cv2.imwrite(mask_path, self.debug_info["orange_mask"])
            print(f"Orange mask saved to: {mask_path}")


def format_result_for_human(result: dict[str, Any]) -> str:
    """Format the detection result for human-readable output."""
    lines = []
    lines.append("=" * 60)
    lines.append("Breadth Chart Detection Results (OpenCV)")
    lines.append("=" * 60)

    lines.append(f"\nImage: {result['image']['path']}")
    lines.append(f"Confidence: {result['confidence'].upper()}")

    lines.append("\n--- Detected Values ---")

    if result["200ma"] is not None:
        lines.append(
            f"200-Day MA: {result['200ma_percent']} ({result.get('200ma_interpretation', 'N/A')})"
        )
    else:
        lines.append("200-Day MA: NOT DETECTED")

    if result["8ma"] is not None:
        lines.append(
            f"8-Day MA:   {result['8ma_percent']} ({result.get('8ma_interpretation', 'N/A')})"
        )
    else:
        lines.append("8-Day MA:   NOT DETECTED")

    lines.append("\n--- Calibration ---")
    cal = result["calibration"]
    lines.append(f"Red line (0.73) Y-pixel: {cal['red_line_y']}")
    lines.append(f"Blue line (0.23) Y-pixel: {cal['blue_line_y']}")
    lines.append(f"Y-scale: {cal.get('y_scale', 'N/A')}")
    lines.append(f"Calibration successful: {cal['calibrated']}")

    if "debug" in result:
        lines.append("\n--- Debug Info ---")
        lines.append(f"Green pixels detected: {result['debug'].get('green_pixel_count', 'N/A')}")
        lines.append(f"Orange pixels detected: {result['debug'].get('orange_pixel_count', 'N/A')}")

    lines.append("\n" + "=" * 60)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Detect 200MA and 8MA values from S&P 500 Breadth Index charts (OpenCV version).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python detect_breadth_values.py charts/2025-12-22/IMG_5499.jpeg
  python detect_breadth_values.py charts/2025-12-22/IMG_5499.jpeg --debug
  python detect_breadth_values.py charts/2025-12-22/IMG_5499.jpeg --json
        """,
    )

    parser.add_argument("image_path", help="Path to the breadth chart image")
    parser.add_argument(
        "--debug", action="store_true", help="Save debug images showing detection process"
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON only")

    args = parser.parse_args()

    if not os.path.isfile(args.image_path):
        print(f"Error: File not found: {args.image_path}", file=sys.stderr)
        sys.exit(1)

    try:
        detector = BreadthChartDetector(args.image_path, debug=args.debug)
        result = detector.analyze()

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(format_result_for_human(result))
            print("\nJSON output:")
            print(json.dumps(result, indent=2))

        # Exit with error code if detection failed
        if result["confidence"] == "failed":
            sys.exit(1)

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
