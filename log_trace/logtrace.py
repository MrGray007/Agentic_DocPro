from datetime import datetime

def log_agent_trace( agent_name, input_data, output_data, metadata=None):
    """
    Appends structured decision trace for Responsible AI logging.
    """

    trace_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent_name,
        "input": input_data,
        "output": output_data,
        "metadata": metadata or {}
    }

    return trace_entry
