from .DisplayConfig import DisplayConfig
from .Shader import load_program, vertex, fragment, fragment_fov, fragment_color
from .Observer import Observer

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

import glm

"""
Uses OpenGL to render 3D graphics of rodents.
"""

class Renderer():

    def __init__(self, config: DisplayConfig):
        self.config = config
        self.shad = None
        self.shad_color = None
        self.sphere = gluNewQuadric()

    def loadTextureModeShaders(self):
        self.shad = load_program(vertex, fragment_fov)
        glUseProgram(self.shad)
        glUniform2f(glGetUniformLocation(self.shad, "screenSize"), config.dimensions[0], config.dimensions[1])
        glUniform1i(glGetUniformLocation(self.shad, "overlay"), 0)
        self.shad_color = load_program(vertex, fragment_color)

    def loadColorModeShaders(self):
        self.shad = load_program(vertex, fragment)
        
    def beginPass(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(*self.config.clear_color)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def endPass(self):
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
                    
    def setObserver(self, observer: Observer):
        glMatrixMode(GL_PROJECTION)
        gluPerspective(observer.camera_fov, (self.config.dimensions[0]/self.config.dimensions[1]), 0.1, 500)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glRotatef(observer.camera_fine_pitch, 1, 0, 0)
        glRotatef(observer.camera_fine_yaw, 0, 1, 0)
        glTranslatef(0, 0, -observer.camera_dist)
        glRotatef(observer.camera_pitch, 1, 0, 0)
        glRotatef(observer.camera_yaw, 0, 1, 0)
        view = glm.mat4(1.0)
        glGetFloatv(GL_MODELVIEW_MATRIX, glm.value_ptr(view))
        glPopMatrix()
        if self.shad_color:
            glUseProgram(self.shad_color)
            glUniformMatrix4fv(glGetUniformLocation(self.shad_color, "view"), 1, GL_FALSE, glm.value_ptr(view))
        glUseProgram(self.shad)
        glUniformMatrix4fv(glGetUniformLocation(self.shad, "view"), 1, GL_FALSE, glm.value_ptr(view))

    def drawCube(self, color: tuple[float, float, float]):
        glBegin(GL_QUADS)
        glColor3f(color[0], color[1], color[2])
        glVertex3f(-1, 1, -1)
        glVertex3f(1, 1, -1)
        glVertex3f(1, 1, 1)
        glVertex3f(-1, 1, 1)
        glVertex3f(-1, -1, -1)
        glVertex3f(1, -1, -1)
        glVertex3f(1, -1, 1)
        glVertex3f(-1, -1, 1)
        glVertex3f(-1,  -1, 1)
        glVertex3f( 1,  -1, 1)
        glVertex3f( 1,   1, 1)
        glVertex3f(-1,   1, 1)
        glVertex3f(-1,  -1, -1)
        glVertex3f( 1,  -1, -1)
        glVertex3f( 1,   1, -1)
        glVertex3f(-1,   1, -1)
        glVertex3f(1, -1, -1 )
        glVertex3f(1,  1, -1 )
        glVertex3f(1,  1,  1 )
        glVertex3f(1, -1,  1 )   
        glVertex3f(-1, -1, -1 )
        glVertex3f(-1,  1, -1 )
        glVertex3f(-1,  1,  1 )
        glVertex3f(-1, -1,  1 )
        glEnd()
    
    def drawBackWalls(self, dims: tuple[float, float, float]):
        # draw box walls with texture overlay
        glUseProgram(self.shad)
        glPushMatrix()
        glLoadIdentity()
        glPushMatrix()
        glScale(dims[0]/2, 0.1, dims[2]/2)
        glTranslate(0, -1, 0)
        self.drawCube(color = (1, 1, 0))
        glPopMatrix()
        glPushMatrix()
        glTranslate(0, 0, -dims[2]/2)
        glScale(dims[0]/2, dims[1]/2, 0.1)
        glTranslate(0, 1, -1)
        self.drawCube(color = (0, 1, 1))
        glPopMatrix()
        glPushMatrix()
        glTranslate(-dims[0]/2, 0, 0)
        glScale(0.10, dims[1]/2, dims[2]/2)
        glTranslate(-1, 1, 0)
        self.drawCube(color = (1, 0, 1))
        glPopMatrix()

        # draw pink guard rails
        glUseProgram(self.shad_color)
        glPushMatrix()
        glTranslate(0, +0.4, -dims[2]/2 + 0.2)
        glScale(dims[2]/2, 0.2, 0.2)
        glTranslate(0, -1, 0)
        self.drawCube(color = (1,0,1))
        glPopMatrix()
        glPushMatrix()
        glTranslate(-dims[2]/2 + 0.2, 0.4,0)
        glScale(0.2, 0.2, dims[2]/2)
        glTranslate(0, -1, 0)
        self.drawCube(color = (1,0,1))
        glPopMatrix()
        glPushMatrix()
        glTranslate(-dims[2]/2 + 0.2, 0,-dims[2]/2 + 0.2)
        glScale(0.2, dims[2]/2, 0.2)
        glTranslate(1, 1, 1)
        self.drawCube(color = (1,0,1))
        glPopMatrix()
        glPopMatrix()
                
    def loadTexture(self, img_data: np.ndarray, width: int, height: int):
        self.texture = glGenTextures(1)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data);
        glGenerateMipmap(GL_TEXTURE_2D);

    def drawBall(self, ball: np.ndarray, color: tuple[float, float, float], ball_radius = 0.25):
        glPushMatrix()
        glTranslate(*ball)
        glColor3f(*color)
        gluSphere(self.sphere, ball_radius, 100, 100)
        glPopMatrix()

    def drawConnection(self, start: np.ndarray, end: np.ndarray):
        direction = np.array(end) - np.array(start)
        scale = np.sqrt(((direction)**2).sum())
        glPushMatrix()
        mat = glm.inverse(glm.lookAt(end, start, glm.vec3(0,1,0)))
        glMultMatrixf(mat.to_list())
        glScale(0.1, 0.1, -scale*0.5)
        glTranslate(0, 0, 1)
        self.drawCube((1,1,1))
        glPopMatrix()
    

        
