# TODO

-- Score counter
-- Food absorb animation
-- Special abilities and weapons
blobs grow individually
bigger blobs move slower
auto zoom
biomes
enemies can consume food
more weapon effects
text that shows when a player can pickup a weapon

respawn food
main menu
Audio
parasites
gameover mechanic
reabsorb blobs at some point

limits on splitting
limits on player size
reset player splits eventually like in agario
redo player.size values. it should also be a float instead of an int

blobs grow individually
    -- only update the size of the blob that eats the food
    -- determine if an enemy can be eaten base on the size of the player blob 
        it collides with 
    - change splitting so that instead of being based on a global
         player size, each blob splits into two and bases everything on its own size
    - bigger blobs move slower that smaller blobs
    - rewrite the function that determines where blobs are going to be spawned
        or actually just move it to the Blob class
