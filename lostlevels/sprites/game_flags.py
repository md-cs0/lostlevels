"""Lost Levels' entity game flags."""

CANNOT_JUMP = (1 << 0)      # The player cannot jump off this entity.
DO_NOT_DELETE = (1 << 1)    # Do not automatically delete game entities if they have scrolled out of frame.