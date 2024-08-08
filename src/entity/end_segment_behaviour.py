from dataclasses import dataclass


@dataclass
class ChangeIndex:
    value: int


class ReverseDirection:
    """Sentinel"""


def get_segment_behaviour_at_the_end_of_the_segment(
    num_segments: int, current_idx: int, is_forward: bool, loop: bool
) -> ChangeIndex | ReverseDirection:

    if num_segments == 1:
        return ReverseDirection()
    assert num_segments > 1

    last_idx = num_segments - 1
    if is_forward:
        return _get_segment_end_result_forward(last_idx, current_idx, loop)
    return _get_segment_end_result_backward(last_idx, current_idx, loop)


def _get_segment_end_result_forward(
    last_idx: int, current_idx: int, loop: bool
) -> ChangeIndex | ReverseDirection:

    is_last_segment = current_idx == last_idx

    if not is_last_segment:
        return ChangeIndex(current_idx + 1)
    assert is_last_segment
    if loop:
        return ChangeIndex(0)
    return ReverseDirection()


def _get_segment_end_result_backward(
    last_idx: int, current_idx: int, loop: bool
) -> ChangeIndex | ReverseDirection:

    is_first_segment = current_idx == 0

    if not is_first_segment:
        return ChangeIndex(current_idx - 1)
    assert is_first_segment
    if loop:
        return ChangeIndex(last_idx)
    return ReverseDirection()
