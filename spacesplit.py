  if keys[pygame.K_ESCAPE]:
        running = False

    moving = player.update(keys, dt)
    if not moving:
        player.speed = pygame.Vector2(0, 0)

    # d = v / t
    player.position += player.speed * dt

    player.render_bar(screen)
    world.render_chunk_outlines(screen, player)

    pygame.display.flip()

pygame.quit()


players = [Player(Vector2(screen.get_width() / 2, screen.get_height() / 2), random.choice(colors))]
world = World(players[0])
