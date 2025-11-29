def evaluate_trigger(trigger_type: str, params: dict | None):
    """
    Return list of user_ids matching the trigger.
    Add your logic per trigger_type.
    """

    if trigger_type == "not_seen_for_hours":
        return users_not_visited_within(params.get("hours", 24))

    if trigger_type == "new_facility_to_visit":
        return users_near_new_facility(params["facility_id"])

    if trigger_type == "stay_exceeding_hours":
        return users_with_long_parking(params["hours"])

    # fallback
    return []
