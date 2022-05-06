from scene import Scene
import taichi as ti
from taichi.math import *
scene = Scene(voxel_edges=0.01, exposure=1)
scene.set_floor(-64, (1.0, 1.0, 1.0))
scene.set_background_color((0.5, 0.5, 0.4))
scene.set_directional_light((1, 1, -1), 0.2, (1, 1, 1))
@ti.func
def rgb(r,g,b):
    return vec3(r/255.0, g/255.0, b/255.0)
@ti.func
def proj_plane(o, n, t, p): 
    y = dot(p-o,n);xz=p-(o+n*y);bt=cross(t,n);return vec3(dot(xz,t), y, dot(xz, bt))
@ti.func
def elli(rx,ry,rz,p1_unused,p2_unused,p3_unused,p):
    r = p/vec3(rx,ry,rz); return ti.sqrt(dot(r,r))<1
@ti.func
def cyli(r1,h,r2,round, cone, hole_unused, p):
    ms=min(r1,min(h,r2));rr=ms*round;rt=mix(cone*(max(ms-rr,0)),0,float(h-p.y)*0.5/h);r=vec2(p.x/r1,p.z/r2)
    d=vec2((r.norm()-1.0)*ms+rt,ti.abs(p.y)-h)+rr; return min(max(d.x,d.y),0.0)+max(d,0.0).norm()-rr<0
@ti.func
def box(x, y, z, round, cone, unused, p):
    ms=min(x,min(y,z));rr=ms*round;rt=mix(cone*(max(ms-rr,0)),0,float(y-p.y)*0.5/y);q=ti.abs(p)-vec3(x-rt,y,z-rt)+rr
    return ti.max(q, 0.0).norm() + ti.min(ti.max(q.x, ti.max(q.y, q.z)), 0.0) - rr< 0
@ti.func
def tri(r1, h, r2, round_unused, cone, vertex, p):
    r = vec3(p.x/r1, p.y, p.z/r2);rt=mix(1.0-cone,1.0,float(h-p.y)*0.5/h);r.z+=(r.x+1)*mix(-0.577, 0.577, vertex)
    q = ti.abs(r); return max(q.y-h,max(q.z*0.866025+r.x*0.5,-r.x)-0.5*rt)< 0
@ti.func
def make(func: ti.template(), p1, p2, p3, p4, p5, p6, pos, dir, up, color, mat, mode):
    max_r = 2 * int(max(p3,max(p1, p2))); dir = normalize(dir); up = normalize(cross(cross(dir, up), dir))
    for i,j,k in ti.ndrange((-max_r,max_r),(-max_r,max_r),(-max_r,max_r)): 
        xyz = proj_plane(vec3(0.0,0.0,0.0), dir, up, vec3(i,j,k))
        if func(p1,p2,p3,p4,p5,p6,xyz):
            if mode == 0: scene.set_voxel(pos + vec3(i,j,k), mat, color) # additive
            if mode == 1: scene.set_voxel(pos + vec3(i,j,k), 0, color) # subtractive
            if mode == 2 and scene.get_voxel(pos + vec3(i,j,k))[0] > 0: scene.set_voxel(pos + vec3(i,j,k), mat, color)
@ti.kernel
def initialize_voxels():
    make(cyli,15.0,11.2,15.0,0.0,0.0,1.0,vec3(3,-46,-1),vec3(0.0,1.0,0.0),vec3(1.0,0.0,0.0),rgb(131,102,8),1,0)
    make(cyli,13.1,11.2,13.1,0.0,0.0,1.0,vec3(3,-46,-1),vec3(0.0,1.0,0.0),vec3(1.0,0.0,0.0),rgb(145,122,49),1,0)
    make(cyli,11.2,11.2,11.2,0.0,0.0,1.0,vec3(3,-46,-1),vec3(0.0,1.0,0.0),vec3(1.0,0.0,0.0),rgb(131,102,8),1,0)
    make(cyli,9.4,11.2,9.4,0.0,0.0,1.0,vec3(3,-46,-1),vec3(0.0,1.0,0.0),vec3(1.0,0.0,0.0),rgb(145,122,49),1,0)
    make(cyli,7.5,11.2,7.5,0.0,0.0,1.0,vec3(3,-46,-1),vec3(0.0,1.0,0.0),vec3(1.0,0.0,0.0),rgb(131,102,8),1,0)
    make(cyli,5.6,11.2,5.6,0.0,0.0,1.0,vec3(3,-46,-1),vec3(0.0,1.0,0.0),vec3(1.0,0.0,0.0),rgb(145,122,49),1,0)
    make(cyli,3.8,11.2,3.8,0.0,0.0,1.0,vec3(3,-46,-1),vec3(0.0,1.0,0.0),vec3(1.0,0.0,0.0),rgb(131,102,8),1,0)
    make(cyli,1.9,11.2,1.9,0.0,0.0,1.0,vec3(3,-46,-1),vec3(0.0,1.0,0.0),vec3(1.0,0.0,0.0),rgb(145,122,49),1,0)
    make(elli,7.5,7.5,7.5,0.0,0.0,0.0,vec3(18,16,-1),vec3(0.0,1.0,0.0),vec3(1.0,0.0,0.1),rgb(255,255,255),1,0)
    make(cyli,1.5,16.6,1.5,0.0,0.0,1.0,vec3(19,-2,0),vec3(-0.1,1.0,-0.0),vec3(1.0,0.1,0.1),rgb(255,255,255),1,0)
    make(cyli,1.5,7.8,1.5,0.0,0.0,1.0,vec3(14,-15,2),vec3(-0.8,0.5,0.2),vec3(0.5,0.9,-0.0),rgb(255,255,255),1,0)
    make(cyli,1.5,15.5,1.5,0.0,0.0,1.0,vec3(9,-26,5),vec3(0.1,-1.0,0.1),vec3(-1.0,-0.1,-0.1),rgb(255,255,255),1,0)
    make(cyli,1.5,11.0,1.5,0.0,0.0,1.0,vec3(20,-28,-5),vec3(-0.0,0.9,0.4),vec3(1.0,0.1,-0.1),rgb(255,255,255),1,0)
    make(cyli,1.5,11.0,1.5,0.0,0.0,1.0,vec3(26,-47,-11),vec3(-0.5,0.9,0.1),vec3(0.9,0.5,-0.1),rgb(255,255,255),1,0)
    make(cyli,1.5,9.4,1.5,0.0,0.0,1.0,vec3(15,2,-8),vec3(-0.6,0.4,-0.7),vec3(0.8,0.1,-0.6),rgb(255,255,255),1,0)
    make(cyli,1.5,6.6,1.5,0.0,0.0,1.0,vec3(17,-4,7),vec3(0.4,0.3,-0.9),vec3(0.9,-0.1,0.4),rgb(255,255,255),1,0)
    make(cyli,1.5,8.3,1.5,0.0,0.0,1.0,vec3(11,-5,5),vec3(-0.5,0.2,-0.9),vec3(0.9,-0.0,-0.5),rgb(255,255,255),1,0)
    make(cyli,1.5,12.0,1.5,0.0,0.0,1.0,vec3(20,-7,0),vec3(-0.1,1.0,-0.0),vec3(1.0,0.1,0.1),rgb(255,255,255),1,0)
    make(cyli,1.5,9.4,1.5,0.0,0.0,1.0,vec3(6,13,-16),vec3(-0.4,0.9,-0.2),vec3(0.4,-0.0,-0.9),rgb(255,255,255),1,0)
    make(cyli,1.5,3.8,1.5,0.0,0.0,0.0,vec3(2,25,-18),vec3(-0.1,1.0,-0.1),vec3(0.4,-0.0,-0.9),rgb(71,71,71),1,0)
    make(box,3.8,1.5,3.8,0.0,0.0,0.0,vec3(2,29,-18),vec3(-0.1,1.0,-0.1),vec3(0.4,-0.0,-0.9),rgb(129,129,129),1,0)
    make(box,3.8,1.5,3.8,0.0,0.0,0.0,vec3(2,29,-18),vec3(-0.1,1.0,-0.1),vec3(0.4,-0.0,-0.9),rgb(126,126,126),1,0)
    make(box,1.5,16.9,2.6,0.0,0.0,0.0,vec3(0,47,-19),vec3(-0.1,1.0,-0.1),vec3(0.4,-0.0,-0.9),rgb(78,78,78),1,0)
    make(box,1.5,15.0,1.5,0.0,0.0,0.0,vec3(0,45,-19),vec3(-0.1,1.0,-0.1),vec3(0.4,-0.0,-0.9),rgb(255,229,0),1,0)
    make(box,1.5,25.8,10.2,0.0,0.0,0.0,vec3(34,-18,1),vec3(-0.5,0.9,-0.1),vec3(0.9,0.5,0.0),rgb(67,67,67),1,0)
    make(box,1.5,24.2,8.3,0.0,0.0,0.0,vec3(34,-18,1),vec3(-0.5,0.9,-0.1),vec3(0.9,0.5,0.0),rgb(149,36,36),1,0)
    make(box,161.7,1.0,161.7,0.0,0.0,0.0,vec3(3,-58,-1),vec3(0.0,1.0,0.0),vec3(1.0,-0.0,-0.0),rgb(58,47,16),1,0)
initialize_voxels()
scene.finish()
