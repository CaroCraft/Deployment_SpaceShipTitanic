import pygame

class Astronauta:

    def __init__(self, x, y, w, h, state="normal"):

        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.state = state

        # Imágenes
        self.image_normal = pygame.image.load("sprites/normal.png").convert_alpha()

        self.image_dormido = pygame.image.load("sprites/dormido.png").convert_alpha()

        self.image_transportado = pygame.image.load("sprites/transportado.png").convert_alpha()

        # el salto
        self.images_no_transportado = [
            pygame.image.load("sprites/salto_1.png").convert_alpha(),
            pygame.image.load("sprites/salto_2.png").convert_alpha(),
            pygame.image.load("sprites/salto_3.png").convert_alpha(),
            pygame.image.load("sprites/salto_4.png").convert_alpha()
        ]

        # Escalar imágenes
        self.image_normal = pygame.transform.scale(
            self.image_normal, (w, h)
        )

        self.image_dormido = pygame.transform.scale(
            self.image_dormido, (w, h)
        )

        self.image_transportado = pygame.transform.scale(
            self.image_transportado, (w, h)
        )

        self.images_no_transportado = [
            pygame.transform.scale(image, (w, h))
            for image in self.images_no_transportado
        ]

        # Imagen actual
        self.image = self.image_normal

        # Variables para animaciones
        self.frame_actual = 0
        self.tiempo_animacion = 0

        self.angulo = 0
        self.rotaciones = 0

    def cambiar_estado(self, nuevo_estado):

        self.state = nuevo_estado

        # Reiniciar animaciones
        self.frame_actual = 0
        self.tiempo_animacion = 0
        self.angulo = 0
        self.rotaciones = 0

        if nuevo_estado == "normal":
            self.image = self.image_normal

        elif nuevo_estado == "dormido":
            self.image = self.image_dormido

        elif nuevo_estado == "transportado":
            self.image = self.image_transportado

        elif nuevo_estado == "no_transportado":
            self.image = self.images_no_transportado[0]

    def actualizar(self, dt, activo):

        # Predicción True

        if self.state == "transportado":

            velocidad = 360

            self.angulo += velocidad * dt

            if self.angulo >= 360:

                self.angulo -= 360
                self.rotaciones += 1

            # Después de 3 vueltas
            if self.rotaciones >= 3:

                if activo:
                    self.cambiar_estado("normal")
                else:
                    self.cambiar_estado("dormido")


        # Aquí cuando la predicción es false 
        
        elif self.state == "no_transportado":

            self.tiempo_animacion += dt

            if self.tiempo_animacion >= 0.2:

                self.tiempo_animacion = 0
                self.frame_actual += 1

                if self.frame_actual >= len(self.images_no_transportado):

                    # Terminó la animación
                    if activo:
                        self.cambiar_estado("normal")
                    else:
                        self.cambiar_estado("dormido")

                else:

                    self.image = self.images_no_transportado[
                        self.frame_actual
                    ]

    def draw(self, surface):

        if self.state == "transportado":

            # Rotar alrededor del centro
            rotated_image = pygame.transform.rotate(
                self.image_transportado,
                self.angulo
            )

            rect = rotated_image.get_rect(
                center=(self.x, self.y)
            )

            surface.blit(rotated_image, rect)

        else:

            rect = self.image.get_rect(
                center=(self.x, self.y)
            )

            surface.blit(self.image, rect)