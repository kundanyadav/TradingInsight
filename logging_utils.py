import json
import os
from datetime import datetime
from typing import Dict, Any, List

LOG_FILE = "history_log.jsonl"


def log_event(event_type: str, data: Dict[str, Any]):
    """Log an event to the JSONL log file."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "data": data,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def read_log_history() -> List[Dict[str, Any]]:
    """Read all log entries from the log file."""
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r") as f:
        return [json.loads(line) for line in f if line.strip()]


def clear_log_history():
    """Clear the log file (for testing or reset)."""
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)


def log_portfolio_summary(summary: Dict[str, Any]):
    log_event("portfolio_summary", summary)


def log_recommendation(recommendation: Dict[str, Any]):
    log_event("recommendation", recommendation)


def log_user_action(action: str, details: Dict[str, Any]):
    log_event(f"user_action:{action}", details)


def analyze_feedback_patterns(n_recent: int = 50) -> dict:
    """
    Analyze recent user feedback to extract preference patterns.
    Returns a dict summarizing accept/reject counts by symbol, option type, rationale keywords, and risk.
    """
    import re
    logs = read_log_history()
    feedback_logs = [log for log in logs if log['event_type'] in ('user_action:accepted', 'user_action:rejected')]
    feedback_logs = feedback_logs[-n_recent:]  # Only recent feedback

    symbol_stats = {}
    option_type_stats = {}
    rationale_keywords = {}
    risk_stats = {'accepted': [], 'rejected': []}

    for log in feedback_logs:
        action = 'accepted' if log['event_type'] == 'user_action:accepted' else 'rejected'
        data = log['data']
        symbol = data.get('symbol', 'UNKNOWN')
        option_type = data.get('option_type', 'UNKNOWN')
        rationale = data.get('rationale', '')
        reason = data.get('reason', '')
        risk = data.get('risk', None)

        # Symbol stats
        if symbol not in symbol_stats:
            symbol_stats[symbol] = {'accepted': 0, 'rejected': 0}
        symbol_stats[symbol][action] += 1

        # Option type stats
        if option_type not in option_type_stats:
            option_type_stats[option_type] = {'accepted': 0, 'rejected': 0}
        option_type_stats[option_type][action] += 1

        # Rationale keywords
        for text in [rationale, reason]:
            for word in re.findall(r'\b\w+\b', text.lower()):
                if word not in rationale_keywords:
                    rationale_keywords[word] = {'accepted': 0, 'rejected': 0}
                rationale_keywords[word][action] += 1

        # Risk stats
        if risk is not None:
            risk_stats[action].append(risk)

    # Summarize risk
    avg_risk = {
        'accepted': sum(risk_stats['accepted']) / len(risk_stats['accepted']) if risk_stats['accepted'] else None,
        'rejected': sum(risk_stats['rejected']) / len(risk_stats['rejected']) if risk_stats['rejected'] else None,
    }

    return {
        'symbol_stats': symbol_stats,
        'option_type_stats': option_type_stats,
        'rationale_keywords': rationale_keywords,
        'avg_risk': avg_risk,
        'total_feedback': len(feedback_logs),
    }


if __name__ == "__main__":
    # Example usage
    clear_log_history()
    log_portfolio_summary({"positions": 5, "pnl": 1234})
    log_recommendation({"text": "Buy RELIANCE 2500CE"})
    log_user_action("accepted", {"recommendation": "Buy RELIANCE 2500CE"})
    print(read_log_history()) 