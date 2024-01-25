from itertools import product

def find_intersection(scenarios):
    # Generate all possible combinations
    all_combinations = list(product(*scenarios))

    # Iterate through all combinations and check for intersections
    result = []
    for combination in all_combinations:
        # Extract time ranges for each element
        time_ranges = [(start, end) for _, _, start, end in combination]

        # Check for intersection
        intersection = [max(starts), min(ends)] if (starts := [start for start, _ in time_ranges]) and (ends := [end for _, end in time_ranges]) and max(starts) <= min(ends) else None

        # If there is an intersection, add the combination and the intersection time range to the result list
        if intersection:
            # Extract egoID
            ego_id = combination[0][0]
            # Extract the list of target IDs
            tgt_ids = [tgt_info[1] for tgt_info in combination[1:]]
            # Add to the result list
            result.append([ego_id, tgt_ids, *intersection])

    return result

# Example usage:
scenarios = [
    [[1, 2, 10, 20], [1, 2, 25, 30]],
    [[1, 3, 12, 28]],
    [[1, 6, 11, 25], [1, 7, 16, 18]]
]

result = find_intersection(scenarios)
print(result)
