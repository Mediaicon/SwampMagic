"""Awareness presentation helpers.

Awareness is NOT a sanity meter (Design Doc ch. 8). It buys perception and costs
belonging. The Green Eye is shown, never explained.
"""
import config


def eye(awareness: int) -> str:
    open_pips = sum(1 for t in config.EYE_THRESHOLDS if awareness >= t)
    shut = len(config.EYE_THRESHOLDS) - open_pips
    return "(" + config.EYE_OPEN * open_pips + config.EYE_SHUT * shut + ")"


def fatigue_label(fatigue: int) -> str:
    label = config.FATIGUE_LABELS[0][1]
    for threshold, name in config.FATIGUE_LABELS:
        if fatigue >= threshold:
            label = name
    return label
