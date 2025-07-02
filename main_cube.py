import math
import time
import random as pyrandom
from vpython import *
from math import degrees
from typing import List


class CubeElement:
    """
    Rappresenta un singolo cubetto all'interno del cubo principale.
    Gestisce colore, rotazione indipendente e pulsazione.
    """

    def __init__(self, pos: vector):
        self.base_pos = pos
        sx = 0.8 + pyrandom.uniform(-0.2, 0.2)
        sy = 0.8 + pyrandom.uniform(-0.2, 0.2)
        sz = 0.8 + pyrandom.uniform(-0.2, 0.2)
        self.box = box(
            pos=self.base_pos, size=vector(sx, sy, sz), color=color.white, opacity=0.95
        )
        self.angleX = 0.0
        self.angleY = 0.0
        self.angleZ = 0.0

    def update(self, t: float, jiggle_mag: float) -> None:
        """
        Applica rotazione casuale, variazione di dimensione e aggiornamento colore.
        """
        axis = pyrandom.choice([vector(1, 0, 0), vector(0, 1, 0), vector(0, 0, 1)])
        angle = pyrandom.uniform(-jiggle_mag, jiggle_mag)
        self.box.rotate(angle=angle, axis=axis, origin=self.box.pos)

        if axis.x:
            self.angleX += angle
        elif axis.y:
            self.angleY += angle
        elif axis.z:
            self.angleZ += angle

        # Colore arcobaleno dinamico
        hue = (math.sin(t + self.base_pos.mag * 0.5) + 1) / 2
        self.box.color = color.hsv_to_rgb(vector(hue, 1, 1))

        # Effetto "pulsazione"
        scale = 0.9 + 0.1 * math.sin(t + self.box.pos.x)
        self.box.size = vector(scale, scale, scale)

    def rotate_global(self, center: vector, axis: vector, angle: float) -> None:
        """
        Ruota il cubetto attorno al centro del cubo principale.
        """
        self.box.pos = center + rotate(self.box.pos - center, angle=angle, axis=axis)


class CubeSimulation:
    """
    Gestisce la simulazione dell'intero cubo animato e dell'HUD tecnico.
    """

    def __init__(
        self,
        sq_num: int = 4,
        sq_size: float = 1.5,
        rot_speed: float = 0.01,
        jiggle_mag: float = 0.02,
    ):
        self.sq_num = sq_num
        self.sq_size = sq_size
        self.rot_speed = rot_speed
        self.jiggle_mag = jiggle_mag
        self.center = vector(0, 0, 0)
        self.cubes: List[CubeElement] = []

        # Riferimenti per calcolo inclinazioni
        self.ref_x = vector(1, 0, 0)
        self.ref_y = vector(0, 1, 0)
        self.ref_z = vector(0, 0, 1)

        # Accumulatori angolari
        self.rot_x = 0.0
        self.rot_y = 0.0
        self.rot_z = 0.0

        # Etichetta HUD
        self.hud = label(
            pos=vector(0, 0, 0),
            text="",
            xoffset=270,
            yoffset=270,
            height=14,
            border=10,
            font="monospace",
            box=True,
            line=False,
            color=color.cyan,
            space=30,
        )

        self._create_scene()
        self._create_cubes()

    def _create_scene(self) -> None:
        """Imposta la scena VPython."""
        scene.background = color.black
        scene.width = 1000
        scene.height = 800
        scene.title = "Cubo CAD Animato"
        scene.forward = vector(-1, -1, -2)

    def _create_cubes(self) -> None:
        """Crea la griglia di cubetti nella scena."""
        for i in range(-self.sq_num, self.sq_num):
            for j in range(-self.sq_num, self.sq_num):
                for k in range(-self.sq_num, self.sq_num):
                    pos = vector(i * self.sq_size, j * self.sq_size, k * self.sq_size)
                    self.cubes.append(CubeElement(pos))

    def _rotate_reference_axes(self) -> None:
        """Ruota gli assi virtuali per tracciare l'inclinazione."""
        self.ref_x = rotate(self.ref_x, angle=self.rot_speed, axis=vector(1, 0, 0))
        self.ref_y = rotate(
            self.ref_y, angle=self.rot_speed * 1.2, axis=vector(0, 1, 0)
        )
        self.ref_z = rotate(
            self.ref_z, angle=self.rot_speed * 0.8, axis=vector(0, 0, 1)
        )

        self.rot_x += self.rot_speed
        self.rot_y += self.rot_speed * 1.2
        self.rot_z += self.rot_speed * 0.8

    def _update_hud(self) -> None:
        """Aggiorna l'HUD con info dimensionali e angolari."""

        positions = [c.box.pos for c in self.cubes]
        min_x, max_x = min(p.x for p in positions), max(p.x for p in positions)
        min_y, max_y = min(p.y for p in positions), max(p.y for p in positions)
        min_z, max_z = min(p.z for p in positions), max(p.z for p in positions)

        dim_x, dim_y, dim_z = max_x - min_x, max_y - min_y, max_z - min_z
        angle_x = degrees(self.rot_x) % 360
        angle_y = degrees(self.rot_y) % 360
        angle_z = degrees(self.rot_z) % 360
        total_cubes = len(self.cubes)

        self.hud.text = (
            f"CUBO 3D DINAMICO (VPython)\n"
            f"Cubi totali: {total_cubes}\n"
            f"\n📦 Dimensioni (unità):\n"
            f"  X: {dim_x:.2f}\n"
            f"  Y: {dim_y:.2f}\n"
            f"  Z: {dim_z:.2f}\n"
            f"\n🌀 Inclinazioni:\n"
            f"  X: {angle_x:.1f}°\n"
            f"  Y: {angle_y:.1f}°\n"
            f"  Z: {angle_z:.1f}°"
        )

    def run(self) -> None:
        """Ciclo principale animazione."""
        while True:
            rate(60)
            t = time.time()
            self._rotate_reference_axes()

            for cube in self.cubes:
                cube.rotate_global(self.center, vector(1, 0, 0), self.rot_speed)
                cube.rotate_global(self.center, vector(0, 1, 0), self.rot_speed * 1.2)
                cube.rotate_global(self.center, vector(0, 0, 1), self.rot_speed * 0.8)
                cube.update(t, self.jiggle_mag)

            self._update_hud()


if __name__ == "__main__":
    simulation = CubeSimulation()
    simulation.run()
