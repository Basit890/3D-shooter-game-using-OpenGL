from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import math
import random

class GameConfig:
    def __init__(self):
        # Ekhaney game er shob settings rakha hoyeche
        self.scr_w = 1000  # Screen er width
        self.scr_h = 800   # Screen er height
        self.arena = 600   # Game arena er size
        self.fov = 120     # Camera er field of view

        # Camera er position and rotation settings
        self.cam_pos = [0, 600, 600]  # Camera kothay ache
        self.cam_rot = 0              # Camera er rotation angle
        self.cam_dist = 600           # Camera er distance from center
        self.cam_elev = 600           # Camera er elevation (upor niche)

        # Player er properties
        self.p_pos = [0, 0, 0]  # Player er position
        self.p_rot = 0          # Player er rotation
        self.p_spd = 10         # Player er movement speed
        self.turn_spd = 5       # Player er turning speed
        self.hp = 5             # Player er health
        self.score = 0          # Player er score

        # Weapon and bullet related settings
        self.bullets = []       # Bullet er list
        self.misses = 0         # Missed shot er count
        self.max_miss = 10      # Maximum allowed missed shots
        self.bullet_sz = 7.5    # Bullet er size
        self.bullet_spd = 1     # Bullet er speed

        # Enemy related settings
        self.enemies = []       # Enemy er list
        self.e_scale = 1.0      # Enemy er size scale
        self.e_timer = 0        # Enemy animation er timer
        self.e_spd = 0.025      # Enemy er movement speed
        self.max_e = 5          # Maximum number of enemies
        self.e_hitbox = 60      # Enemy er hitbox size

        # Game state flags
        self.fp = False         # First person view on/off
        self.auto_shoot = False # Auto shooting on/off
        self.auto_aim = False   # Auto aiming on/off
        self.over = False       # Game over status

class GameRenderer:
    def __init__(self, cfg):
        self.cfg = cfg  # Game config store kore
        self.wpn_off = [30, 15, 80]  # Weapon er offset position

    def show_text(self, x, y, text, font=GLUT_BITMAP_HELVETICA_18):
        # Screen e text dekhay specific position e
        glColor3f(1, 1, 1)  # Text er color white
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()      # Current projection matrix save kore
        glLoadIdentity()    # Projection matrix reset kore
        # 2D text render korar jonno orthographic projection set kore
        gluOrtho2D(0, self.cfg.scr_w, 0, self.cfg.scr_h)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()      # Current modelview matrix save kore
        glLoadIdentity()    # Modelview matrix reset kore

        glRasterPos2f(x, y) # Text er position set kore
        # Text er prottek character render kore
        for ch in text:
            glutBitmapCharacter(font, ord(ch))

        glPopMatrix()       # Modelview matrix restore kore
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()       # Projection matrix restore kore
        glMatrixMode(GL_MODELVIEW)  # Modelview matrix e fire jay

    def draw_arena(self):
        # Game arena er floor and walls draw kore
        glBegin(GL_QUADS)

        # Floor er tiles checkerboard pattern e draw kore
        for i in range(-self.cfg.arena, self.cfg.arena + 1, 100):
            for j in range(-self.cfg.arena, self.cfg.arena + 1, 100):
                # Checkerboard pattern er jonno alternate color use kore
                glColor3f(1, 1, 1) if (i + j) % 200 == 0 else glColor3f(0.7, 0.5, 0.95)
                glVertex3f(i, j, 0)
                glVertex3f(i + 100, j, 0)
                glVertex3f(i + 100, j + 100, 0)
                glVertex3f(i, j + 100, 0)

        # Boundary walls different color e draw kore
        colors = [(0,1,0), (0,0,1), (1,1,1), (0,1,1)]
        walls = [
            [(-self.cfg.arena, -self.cfg.arena), (-self.cfg.arena, self.cfg.arena+100)],
            [(self.cfg.arena+100, -self.cfg.arena), (self.cfg.arena+100, self.cfg.arena+100)],
            [(-self.cfg.arena, self.cfg.arena+100), (self.cfg.arena+100, self.cfg.arena+100)],
            [(-self.cfg.arena, -self.cfg.arena), (self.cfg.arena+100, -self.cfg.arena)]
        ]

        # Prottek wall nijeswo color e draw kore
        for idx, wall in enumerate(walls):
            glColor3f(*colors[idx])
            glVertex3f(wall[0][0], wall[0][1], 0)
            glVertex3f(wall[1][0], wall[1][1], 0)
            glVertex3f(wall[1][0], wall[1][1], 100)
            glVertex3f(wall[0][0], wall[0][1], 100)

        glEnd()

    def setup_view(self):
        # Camera view set kore
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()    # Projection matrix reset kore
        # Perspective projection set kore
        gluPerspective(self.cfg.fov,
                      float(self.cfg.scr_w)/self.cfg.scr_h,
                      0.1, 1500)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()    # Modelview matrix reset kore

        if self.cfg.fp:
            # First person view setup kore
            angle = math.radians(self.cfg.p_rot)
            # Player position and weapon offset use kore eye position calculate kore
            eye_x = self.cfg.p_pos[0] + self.wpn_off[0]/2 * math.sin(angle) - self.wpn_off[1] * math.cos(angle)
            eye_y = self.cfg.p_pos[1] - self.wpn_off[0]/2 * math.cos(angle) - self.wpn_off[1] * math.sin(angle)
            eye_z = self.cfg.p_pos[2] + self.wpn_off[2] + 20

            # Auto-shoot without auto-aim er jonno special case
            if self.cfg.auto_shoot and not self.cfg.auto_aim:
                eye_x, eye_y, eye_z = self.cfg.p_pos[0], self.cfg.p_pos[1], self.cfg.p_pos[2] + 160

            # Look-at point calculate kore
            look_x = eye_x - math.sin(-angle) * 100
            look_y = eye_y - math.cos(-angle) * 100
            gluLookAt(eye_x, eye_y, eye_z, look_x, look_y, eye_z, 0, 0, 1)
        else:
            # Third person view setup kore
            angle = math.radians(self.cfg.cam_rot)
            # Camera position calculate kore distance and angle er upor
            cam_x = self.cfg.cam_dist * math.sin(angle)
            cam_y = self.cfg.cam_dist * math.cos(angle)
            gluLookAt(cam_x, cam_y, self.cfg.cam_elev, 0, 0, 0, 0, 0, 1)

    def draw_player(self):
        # Player character draw kore
        glPushMatrix()
        # Player ke world e position and rotate kore
        glTranslatef(*self.cfg.p_pos)
        glRotatef(self.cfg.p_rot, 0, 0, 1)

        # Game over hole player ke shuye dekhay
        if self.cfg.over:
            glRotatef(-90, 1, 0, 0)

        # Right leg draw kore
        glPushMatrix()
        glTranslatef(0, -60, 15)  # Right leg at player’s origin
        glColor3f(0.0, 0.0, 1.0)   # Blue color
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 5, 10, 50, 10, 10)
        glPopMatrix()

        # Left leg draw kore
        glPushMatrix()
        glTranslatef(30, -60, 15)  # Left leg 30 units to the right
        glColor3f(0.0, 0.0, 1.0)   # Blue color
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 5, 10, 50, 10, 10)
        glPopMatrix()

        # Body draw kore
        glPushMatrix()
        glTranslatef(15, 0, 50)
        glColor3f(85/255, 108/255, 47/255)  # Olive green color
        glutSolidCube(40)

        # Head draw kore
        glPushMatrix()
        glTranslatef(0, 0, 40)
        glColor3f(0.0, 0.0, 0.0)   # Black color
        gluSphere(gluNewQuadric(), 20, 10, 10)
        glPopMatrix()

        # Left arm draw kore
        glPushMatrix()
        glTranslatef(20, -60, 25)
        glRotatef(-90, 1, 0, 0)
        glColor3f(254/255, 223/255, 188/255)  # Skin color
        gluCylinder(gluNewQuadric(), 4, 8, 50, 10, 10)
        glPopMatrix()

        # Right arm draw kore
        glPushMatrix()
        glTranslatef(-20, -60, 25)
        glRotatef(-90, 1, 0, 0)
        glColor3f(254/255, 223/255, 188/255)  # Skin color
        gluCylinder(gluNewQuadric(), 4, 8, 50, 10, 10)
        glPopMatrix()

        # Weapon draw kore
        glPushMatrix()
        glTranslatef(0, -90, 0)  # Weapon ke chest er center e position kore
        glRotatef(-90, 1, 0, 0)  # Weapon ke rotate kore
        glColor3f(192/255, 192/255, 192/255)  # Silver color set kore
        gluCylinder(gluNewQuadric(), 1, 10, 80, 10, 10)  # Cylinder draw kore as weapon
        glPopMatrix()

        glPopMatrix()
        glPopMatrix()

    def draw_projectile(self, x, y, z):
        # Specific position e bullet draw kore
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(-90, 1, 0, 0)
        glColor3f(1, 0, 0)  # Red color
        glutSolidCube(self.cfg.bullet_sz)
        glPopMatrix()

    def draw_enemy(self, x, y, z):
        # Specific position e enemy draw kore
        glPushMatrix()
        glTranslatef(x, y, z + 35)
        # Animation er jonno scale apply kore
        glScalef(self.cfg.e_scale, self.cfg.e_scale, self.cfg.e_scale)
        glColor3f(1, 0, 0)  # Red color for body
        gluSphere(gluNewQuadric(), 35, 10, 10)
        glTranslatef(0, 0, 50)
        glColor3f(0, 0, 0)  # Black color for head
        gluSphere(gluNewQuadric(), 15, 10, 10)
        glPopMatrix()

class GameLogic:
    def __init__(self, cfg, rend):
        self.cfg = cfg    # Game config store kore
        self.rend = rend  # Renderer store kore

    def fire_weapon(self):
        # Notun bullet create kore
        angle = math.radians(self.cfg.p_rot + (45 if self.cfg.fp else -90))

        if self.cfg.fp:
            # First person view te bullet er starting position
            x = self.cfg.p_pos[0] + self.rend.wpn_off[0] * math.sin(angle) - self.rend.wpn_off[1] * math.cos(angle)
            y = self.cfg.p_pos[1] - self.rend.wpn_off[0] * math.cos(angle) - self.rend.wpn_off[1] * math.sin(angle)
            z = self.cfg.p_pos[2] + self.rend.wpn_off[2]
        else:
            # Third person view te bullet er starting position
            offset_x = self.rend.wpn_off[0] * math.cos(angle) - self.rend.wpn_off[1] * math.sin(angle)
            offset_y = self.rend.wpn_off[0] * math.sin(angle) + self.rend.wpn_off[1] * math.cos(angle)
            x = self.cfg.p_pos[0] + offset_x
            y = self.cfg.p_pos[1] + offset_y
            z = self.cfg.p_pos[2] + self.rend.wpn_off[2]

        # Bullet ke list e add kore
        self.cfg.bullets.append([x, y, z, self.cfg.p_rot])

    def update_projectiles(self):
        # Bullet er position update kore and arena er baire gele remove kore
        to_remove = []

        for bullet in self.cfg.bullets:
            # Bullet ke tar direction e move kore
            angle = math.radians(bullet[3] - 90)
            bullet[0] += self.cfg.bullet_spd * math.cos(angle)
            bullet[1] += self.cfg.bullet_spd * math.sin(angle)

            # Bullet arena er baire gele check kore
            if (bullet[0] > self.cfg.arena + 100 or
                bullet[0] < -self.cfg.arena or
                bullet[1] > self.cfg.arena + 100 or
                bullet[1] < -self.cfg.arena):
                to_remove.append(bullet)
                self.cfg.misses += 1
                # Max missed shots check kore
                if self.cfg.misses >= self.cfg.max_miss:
                    self.cfg.over = True

        # Out of bounds bullet remove kore
        for bullet in to_remove:
            self.cfg.bullets.remove(bullet)

    def check_collisions(self):
        # Bullet and enemy er collision check kore
        hit_enemies = []
        hit_bullets = []

        for bullet in self.cfg.bullets:
            for enemy in self.cfg.enemies:
                # Bullet and enemy er distance calculate kore
                dx = bullet[0] - enemy[0]
                dy = bullet[1] - enemy[1]
                distance = (dx**2 + dy**2) ** 0.5

                # Bullet enemy ke hit koreche kina check kore
                if distance <= self.cfg.e_hitbox:
                    hit_enemies.append(enemy)
                    hit_bullets.append(bullet)
                    self.cfg.score += 1
                    break

        # Hit enemy remove kore and notun spawn kore
        for enemy in hit_enemies:
            self.cfg.enemies.remove(enemy)
            self.spawn_enemies(1)

        # Hit bullet remove kore
        for bullet in hit_bullets:
            self.cfg.bullets.remove(bullet)

        # Player and enemy er collision check kore
        to_remove = []
        for enemy in self.cfg.enemies:
            # Player and enemy er distance calculate kore
            dx = self.cfg.p_pos[0] - enemy[0]
            dy = self.cfg.p_pos[1] - enemy[1]
            distance = (dx**2 + dy**2) ** 0.5

            # Enemy player ke hit koreche kina check kore
            if distance < 50:
                self.cfg.hp -= 1
                to_remove.append(enemy)
                # Player er health shesh hole game over
                if self.cfg.hp <= 0:
                    self.cfg.over = True
                    break

        # Player ke hit kora enemy remove kore and notun spawn kore
        for enemy in to_remove:
            self.cfg.enemies.remove(enemy)
            self.spawn_enemies(1)

    def spawn_enemies(self, count=1):
        # Random position e notun enemy spawn kore
        for _ in range(count):
            while True:
                # Random position generate kore
                x = random.uniform(-self.cfg.arena + 100, self.cfg.arena - 100)
                y = random.uniform(-self.cfg.arena + 100, self.cfg.arena - 100)
                # Enemy player er kache na thake ensure kore
                if (abs(x - self.cfg.p_pos[0]) > 200 and
                    abs(y - self.cfg.p_pos[1]) > 200):
                    self.cfg.enemies.append([x, y, 0])
                    break

    def update_enemies(self):
        # Enemy ke player er dike move kore
        for enemy in self.cfg.enemies:
            # Player er direction calculate kore
            dx = self.cfg.p_pos[0] - enemy[0]
            dy = self.cfg.p_pos[1] - enemy[1]
            angle = math.atan2(dy, dx)
            # Enemy ke oi direction e move kore
            enemy[0] += self.cfg.e_spd * math.cos(angle)
            enemy[1] += self.cfg.e_spd * math.sin(angle)

    def animate_enemies(self):
        # Enemy er size sine wave use kore animate kore
        self.cfg.e_timer += 0.01
        self.cfg.e_scale = 1.0 + 0.5 * math.sin(self.cfg.e_timer)

    def auto_aim(self):
        # Auto aim enable thakle closest enemy te aim kore
        if not self.cfg.enemies or not self.cfg.auto_shoot:
            return

        closest = None
        min_diff = 360

        # Closest enemy er angle find kore
        for enemy in self.cfg.enemies:
            dx = self.cfg.p_pos[0] - enemy[0]
            dy = self.cfg.p_pos[1] - enemy[1]
            angle = math.degrees(math.atan2(dy, dx)) % 360
            diff = min((self.cfg.p_rot - angle) % 360,
                      (angle - self.cfg.p_rot) % 360)

            if diff < min_diff:
                min_diff = diff
                closest = angle

        # Closest enemy te rotate kore and aim thik thakle fire kore
        if closest is not None:
            self.cfg.p_rot = (self.cfg.p_rot + self.cfg.turn_spd/50) % 360
            tolerance = 0.025 if self.cfg.fp else 0.05
            if min_diff <= tolerance:
                self.fire_weapon()

class GameController:
    def __init__(self):
        # Game er shob component initialize kore
        self.cfg = GameConfig()
        self.rend = GameRenderer(self.cfg)
        self.logic = GameLogic(self.cfg, self.rend)

    def keyboard_handler(self, key, *args):
        # Keyboard input handle kore
        x, y = self.cfg.p_pos[0], self.cfg.p_pos[1]

        if not self.cfg.over:
            if key == b'w':
                # Player ke forward move kore
                angle = math.radians(-self.cfg.p_rot)
                x -= self.cfg.p_spd * math.sin(angle)
                y -= self.cfg.p_spd * math.cos(angle)
            elif key == b's':
                # Player ke backward move kore
                angle = math.radians(-self.cfg.p_rot)
                x += self.cfg.p_spd * math.sin(angle)
                y += self.cfg.p_spd * math.cos(angle)
            elif key == b'a':
                # Player ke left turn kore
                self.cfg.p_rot += self.cfg.turn_spd
            elif key == b'd':
                # Player ke right turn kore
                self.cfg.p_rot -= self.cfg.turn_spd
            elif key == b'c':
                # Auto shoot toggle kore
                self.cfg.auto_shoot = not self.cfg.auto_shoot
                self.cfg.e_hitbox = 40 if self.cfg.auto_shoot else 60
            elif key == b'v' and self.cfg.fp and self.cfg.auto_shoot:
                # Auto aim toggle kore (first person and auto shoot on thakle)
                self.cfg.auto_aim = not self.cfg.auto_aim

        if key == b'r':
            # Game reset kore
            self.reset_game()

        # Player ke arena er moddhe rakhe
        self.cfg.p_pos[0] = max(-self.cfg.arena,
                               min(self.cfg.arena + 100, x))
        self.cfg.p_pos[1] = max(-self.cfg.arena,
                               min(self.cfg.arena + 100, y))

    def special_key_handler(self, key, *args):
        # Special keys (arrow keys) handle kore
        if key == GLUT_KEY_UP:
            # Camera ke kache ane
            self.cfg.cam_elev -= 10
            self.cfg.cam_dist -= 10
        elif key == GLUT_KEY_DOWN:
            # Camera ke dure shore
            self.cfg.cam_elev += 10
            self.cfg.cam_dist += 10
        elif key == GLUT_KEY_LEFT:
            # Camera ke left rotate kore
            self.cfg.cam_rot -= 5
        elif key == GLUT_KEY_RIGHT:
            # Camera ke right rotate kore
            self.cfg.cam_rot += 5

    def mouse_handler(self, button, state, x, y):
        # Mouse click handle kore
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not self.cfg.over:
            # Left click weapon fire kore
            self.logic.fire_weapon()

        if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN and not self.cfg.over:
            # Right click first person view toggle kore
            self.cfg.fp = not self.cfg.fp
            self.cfg.auto_aim = False
            self.cfg.turn_spd = 2.5 if self.cfg.fp else 5

    def reset_game(self):
        # Game ke initial state e reset kore
        self.cfg.__init__()
        self.logic.spawn_enemies(self.cfg.max_e)

    def render_scene(self):
        # Game scene render kore
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glViewport(0, 0, self.cfg.scr_w, self.cfg.scr_h)

        # Camera view set kore
        self.rend.setup_view()
        # Game elements draw kore
        self.rend.draw_arena()
        self.rend.draw_player()

        if not self.cfg.over:
            # Auto aim handle kore if enabled
            if self.cfg.auto_shoot:
                self.logic.auto_aim()

            # Enemy draw kore
            for enemy in self.cfg.enemies:
                self.rend.draw_enemy(*enemy)

            # Bullet draw kore
            for bullet in self.cfg.bullets:
                self.rend.draw_projectile(*bullet[:3])

            # Game stats display kore
            self.rend.show_text(10, 770, f"Player Life: {self.cfg.hp}")
            self.rend.show_text(10, 740, f"Score: {self.cfg.score}")
            self.rend.show_text(10, 710, f"Misses: {self.cfg.misses}")
        else:
            # Game over message display kore
            self.rend.show_text(10, 770, f"Game Over! Score: {self.cfg.score}")
            self.rend.show_text(10, 740, 'Press "R" to restart')

        glutSwapBuffers()

    def game_loop(self):
        if not self.cfg.over:
            self.logic.update_enemies()
            self.logic.animate_enemies()
            self.logic.update_projectiles()
            self.logic.check_collisions()
        glutPostRedisplay()

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(1000, 800)
glutCreateWindow(b"3D Shooter Game")
glEnable(GL_DEPTH_TEST)
game = GameController()
game.logic.spawn_enemies(game.cfg.max_e)
glutDisplayFunc(game.render_scene)
glutIdleFunc(game.game_loop)
glutKeyboardFunc(game.keyboard_handler)
glutSpecialFunc(game.special_key_handler)
glutMouseFunc(game.mouse_handler)
game.cfg.e_spd += .10  # Enemy speed increase kore challenge er jonno
glutMainLoop()