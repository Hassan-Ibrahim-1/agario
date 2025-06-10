# TODO

Matthew
    - bigger blobs move slower | CHECK
        you'll have to remove player.position and rework camera.target
        to be able to do this because of the way the camera works rn

    - redo camera target / player.position | CHECK
        try splitting into multiple blobs first
        when all but one of a players blobs are eaten camera target / player.postion
        messes up and stuff like food attracting also gets bugged.

        also remove player.position since its not needed any more
        but try and figure out what to set the camera target to.

        camera currently works by tracking player.position, but the blobs
        each have their own position. it should track something like their center of mass
        instead of player.position which can be offset in weird ways

    - auto zoom | AUTO CAP DONE
    - limit on blob count | DONE, BUT BLOB SPLITTING SEEMS BROKEN
    - reabsorb blobs at some point | DONE, SMALLEST BLOB REABSORBED AFTER A MINUTE
    - respawn food | DONE


    - prevent player from going out of bounds | KINDA DONE
    - don't spawn enemies in player starting chunk | KINDA DONE

Arthur
    - add more weapons and effects
    - text that shows when a player can pickup a weapon
    - Audio
    - parasites
    - add a main menu background

-- Score counter
-- Food absorb animation
-- Special abilities and weapons
-- blobs grow individually
-- enemies can consume food

-- gameover mechanic
-- main menu
