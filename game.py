"""
Misty Moon Treasure Hunt
Features: 4 algorithms (DFS/BFS/A*/GA), Predictive replanning, Subsumption architecture
"""
import pygame, random, math, time, heapq, copy
from collections import deque
from enum import Enum

CELL_SIZE = 40
GRID_WIDTH = 20
GRID_HEIGHT = 15
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE + 60
FPS = 10

COLOR_BG=(15,15,30); COLOR_WALL=(60,60,80); COLOR_FLOOR=(30,30,50)
COLOR_FOG=(10,10,20); COLOR_AGENT=(0,200,255); COLOR_TREASURE=(255,215,0)
COLOR_GUARD=(255,60,60); COLOR_EXPLORED=(50,50,70); COLOR_START=(100,255,180)
COLOR_HUD_BG=(20,20,40); COLOR_TEXT=(200,200,220)

class Cell(Enum):
    FLOOR=0; WALL=1; START=2; TREASURE=3

def heuristic(a,b): return abs(a[0]-b[0])+abs(a[1]-b[1])

def get_neighbors(pos,grid,w,h,guards=None):
    x,y=pos; nb=[]
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if 0<=nx<w and 0<=ny<h and grid[ny][nx]!=Cell.WALL:
            if guards and (nx,ny) in guards: continue
            nb.append((nx,ny))
    return nb

def reconstruct_path(cf,cur):
    p=[cur]
    while cur in cf: cur=cf[cur]; p.append(cur)
    p.reverse(); return p

def astar_search(grid,start,goal,w,h,guards=None):
    t0=time.perf_counter(); ops=[]; heapq.heappush(ops,(0,start))
    cf={}; gs={start:0}; fs={start:heuristic(start,goal)}; exp=set(); ne=0
    while ops:
        _,cur=heapq.heappop(ops)
        if cur in exp: continue
        exp.add(cur); ne+=1
        if cur==goal: return reconstruct_path(cf,cur),ne,time.perf_counter()-t0,exp
        for nb in get_neighbors(cur,grid,w,h,guards):
            tg=gs[cur]+1
            if tg<gs.get(nb,float('inf')):
                cf[nb]=cur; gs[nb]=tg; fs[nb]=tg+heuristic(nb,goal)
                heapq.heappush(ops,(fs[nb],nb))
    return None,ne,time.perf_counter()-t0,exp

def bfs_search(grid,start,goal,w,h,guards=None):
    t0=time.perf_counter(); q=deque([start]); cf={}; vis={start}; ne=0
    while q:
        cur=q.popleft(); ne+=1
        if cur==goal: return reconstruct_path(cf,cur),ne,time.perf_counter()-t0,vis
        for nb in get_neighbors(cur,grid,w,h,guards):
            if nb not in vis: vis.add(nb); cf[nb]=cur; q.append(nb)
    return None,ne,time.perf_counter()-t0,vis

def dfs_search(grid,start,goal,w,h,guards=None):
    t0=time.perf_counter(); stk=[start]; cf={}; vis=set(); ne=0
    while stk:
        cur=stk.pop()
        if cur in vis: continue
        vis.add(cur); ne+=1
        if cur==goal: return reconstruct_path(cf,cur),ne,time.perf_counter()-t0,vis
        for nb in get_neighbors(cur,grid,w,h,guards):
            if nb not in vis: cf[nb]=cur; stk.append(nb)
    return None,ne,time.perf_counter()-t0,vis

def genetic_search(grid,start,goal,w,h,guards=None,pop_size=80,gens=150,mut_rate=0.15):
    t0=time.perf_counter(); exp=set([start]); ne=0
    max_len=w+h+20; dirs=[(0,-1),(0,1),(-1,0),(1,0)]
    def walkable(x,y):
        if 0<=x<w and 0<=y<h and grid[y][x]!=Cell.WALL:
            if guards and (x,y) in guards: return False
            return True
        return False
    def decode(ch):
        path=[start]; cx,cy=start
        for g in ch:
            dx,dy=dirs[g]; nx,ny=cx+dx,cy+dy
            if walkable(nx,ny): cx,cy=nx,ny; path.append((cx,cy)); exp.add((cx,cy))
            if (cx,cy)==goal: break
        return path
    def fitness(ch):
        p=decode(ch); end=p[-1]; d=heuristic(end,goal)
        return d+len(p)*0.1+(0 if end==goal else 500)+(len(p)-len(set(p)))*2
    def make_chrom():
        ch=[]; cx,cy=start
        for _ in range(max_len):
            if random.random()<0.6:
                dx,dy=goal[0]-cx,goal[1]-cy
                g=(3 if dx>0 else 2) if abs(dx)>abs(dy) else (1 if dy>0 else 0)
            else: g=random.randint(0,3)
            ch.append(g); ddx,ddy=dirs[g]; nx,ny=cx+ddx,cy+ddy
            if walkable(nx,ny): cx,cy=nx,ny
            if (cx,cy)==goal: break
        return ch
    pop=[make_chrom() for _ in range(pop_size)]; best_p=None; best_f=float('inf')
    for gen in range(gens):
        scored=sorted([(fitness(c),c) for c in pop],key=lambda x:x[0]); ne+=pop_size
        if scored[0][0]<best_f: best_f=scored[0][0]; best_p=decode(scored[0][1])
        if best_p and best_p[-1]==goal:
            for i,p in enumerate(best_p):
                if p==goal: best_p=best_p[:i+1]; break
            return best_p,ne,time.perf_counter()-t0,exp
        surv=[c for _,c in scored[:int(pop_size*0.3)]]; new=surv[:]
        while len(new)<pop_size:
            p1,p2=random.choice(surv),random.choice(surv)
            ml=min(len(p1),len(p2))
            if ml>=2:
                pt=random.randint(1,ml-1); c1=p1[:pt]+p2[pt:]
            else: c1=p1[:]
            new.append([random.randint(0,3) if random.random()<mut_rate else g for g in c1])
        for _ in range(max(2,pop_size//10)):
            if len(new)<pop_size: new.append(make_chrom())
        pop=new[:pop_size]
    t1=time.perf_counter()
    if best_p:
        if best_p[-1]==goal:
            for i,p in enumerate(best_p):
                if p==goal: best_p=best_p[:i+1]; break
        return best_p,ne,t1-t0,exp
    return None,ne,t1-t0,exp

ALGORITHMS={"A*":astar_search,"BFS":bfs_search,"DFS":dfs_search,"GA":genetic_search}

def generate_map(w,h,wd=0.25,seed=None):
    if seed is not None: random.seed(seed)
    while True:
        grid=[[Cell.FLOOR for _ in range(w)] for _ in range(h)]
        for y in range(h):
            for x in range(w):
                if random.random()<wd: grid[y][x]=Cell.WALL
        s=(1,1); t=(w-2,h-2); grid[s[1]][s[0]]=Cell.START; grid[t[1]][t[0]]=Cell.TREASURE
        for dx in range(-1,2):
            for dy in range(-1,2):
                for px,py in [(s[0]+dx,s[1]+dy),(t[0]+dx,t[1]+dy)]:
                    if 0<=px<w and 0<=py<h and grid[py][px]==Cell.WALL: grid[py][px]=Cell.FLOOR
        p,_,_,_=bfs_search(grid,s,t,w,h)
        if p: return grid,s,t

class Guard:
    def __init__(self,x,y,grid,w,h):
        self.x=x;self.y=y;self.grid=grid;self.width=w;self.height=h
        self.direction=random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        self.steps_in_dir=0;self.max_steps=random.randint(2,5)
        self.history=[(x,y)];self.max_history=10
    def move(self,others):
        self.steps_in_dir+=1
        if self.steps_in_dir>=self.max_steps or random.random()<0.2:
            self.direction=random.choice([(1,0),(-1,0),(0,1),(0,-1)])
            self.steps_in_dir=0;self.max_steps=random.randint(2,5)
        nx,ny=self.x+self.direction[0],self.y+self.direction[1]
        if 0<=nx<self.width and 0<=ny<self.height and self.grid[ny][nx]!=Cell.WALL and (nx,ny) not in others:
            self.x=nx;self.y=ny
        else:
            self.direction=random.choice([(1,0),(-1,0),(0,1),(0,-1)]);self.steps_in_dir=0
        self.history.append((self.x,self.y))
        if len(self.history)>self.max_history: self.history.pop(0)
    def get_pos(self): return (self.x,self.y)
    def predict_future_positions(self,steps=3):
        pred=set([self.get_pos()]); cx,cy=self.x,self.y; dx,dy=self.direction
        for s in range(1,steps+1):
            nx,ny=cx+dx*s,cy+dy*s
            if 0<=nx<self.width and 0<=ny<self.height and self.grid[ny][nx]!=Cell.WALL:
                pred.add((nx,ny))
            for ddx,ddy in [(-1,0),(1,0),(0,-1),(0,1)]:
                px,py=self.x+ddx*s,self.y+ddy*s
                if 0<=px<self.width and 0<=py<self.height and self.grid[py][px]!=Cell.WALL:
                    pred.add((px,py))
        return pred

def place_guards(grid,w,h,n,start,treasure):
    guards=[];occ={start,treasure};att=0
    while len(guards)<n and att<1000:
        x,y=random.randint(0,w-1),random.randint(0,h-1)
        if grid[y][x]==Cell.FLOOR and (x,y) not in occ:
            if abs(x-start[0])+abs(y-start[1])>3 and abs(x-treasure[0])+abs(y-treasure[1])>3:
                guards.append(Guard(x,y,grid,w,h));occ.add((x,y))
        att+=1
    return guards

# === Subsumption Architecture ===
class EmergencyEvadeLayer:
    def __init__(self): self.name="emergency_evade";self.priority=0;self.active=False;self.evade_count=0;self.danger_radius=2
    def evaluate(self,agent,gs):
        ax,ay=agent.x,agent.y
        for gp in gs["guard_positions"]:
            if abs(ax-gp[0])+abs(ay-gp[1])<=self.danger_radius: self.active=True; return True
        self.active=False; return False
    def get_action(self,agent,gs):
        ax,ay=agent.x,agent.y; nearest=None; md=float('inf')
        for gp in gs["guard_positions"]:
            d=abs(ax-gp[0])+abs(ay-gp[1])
            if d<md: md=d; nearest=gp
        if not nearest: return None
        best=None; bd=-1
        for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx,ny=ax+dx,ay+dy
            if 0<=nx<gs["width"] and 0<=ny<gs["height"] and gs["grid"][ny][nx]!=Cell.WALL and (nx,ny) not in gs["guard_positions"]:
                d=abs(nx-nearest[0])+abs(ny-nearest[1])
                if d>bd: bd=d; best=(nx,ny)
        if best: self.evade_count+=1
        return best

class PredictiveReplanLayer:
    def __init__(self): self.name="predictive_replan";self.priority=1;self.active=False;self.horizon=3;self.triggered=False
    def evaluate(self,agent,gs):
        if not agent.path or agent.path_index>=len(agent.path): self.active=False; return False
        rem=set(agent.path[agent.path_index:min(agent.path_index+5,len(agent.path))])
        for g in gs["guards"]:
            if g.predict_future_positions(self.horizon)&rem: self.active=True;self.triggered=True; return True
        self.active=False; return False
    def get_action(self,agent,gs):
        if not self.triggered: return "replan"
        dz=set(gs["guard_positions"])
        for g in gs["guards"]: dz.update(g.predict_future_positions(self.horizon))
        self.triggered=False; return ("predictive_replan",dz)

class FollowPathLayer:
    def __init__(self): self.name="follow_path";self.priority=2;self.active=False
    def evaluate(self,agent,gs):
        self.active=bool(agent.path and agent.path_index<len(agent.path)); return self.active
    def get_action(self,agent,gs):
        if agent.path and agent.path_index<len(agent.path): return agent.path[agent.path_index]
        return None

class ExploreLayer:
    def __init__(self): self.name="explore";self.priority=3;self.active=False
    def evaluate(self,agent,gs):
        self.active=not agent.path or agent.path_index>=len(agent.path); return self.active
    def get_action(self,agent,gs):
        nbs=get_neighbors((agent.x,agent.y),gs["grid"],gs["width"],gs["height"],gs["guard_positions"])
        if nbs:
            uv=[n for n in nbs if n not in agent.explored_cells]
            return random.choice(uv) if uv else random.choice(nbs)
        return None

class SubsumptionController:
    def __init__(self):
        self.layers=[EmergencyEvadeLayer(),PredictiveReplanLayer(),FollowPathLayer(),ExploreLayer()]
        self.active_layer_name="none";self.evade_activations=0;self.predictive_replans=0
    def decide(self,agent,gs):
        for l in self.layers:
            if l.evaluate(agent,gs):
                a=l.get_action(agent,gs); self.active_layer_name=l.name
                if l.name=="emergency_evade": self.evade_activations+=1
                elif l.name=="predictive_replan": self.predictive_replans+=1
                return a,l.name
        self.active_layer_name="idle"; return None,"idle"

class Agent:
    def __init__(self,start,algo_name="A*"):
        self.x,self.y=start;self.start=start;self.algorithm_name=algo_name
        self.algorithm=ALGORITHMS[algo_name];self.path=[];self.path_index=0
        self.total_steps=0;self.total_nodes_explored=0;self.total_compute_time=0.0
        self.replan_count=0;self.predictive_replan_count=0;self.evade_count=0
        self.found_treasure=False;self.explored_cells=set([start]);self.needs_replan=True
        self.subsumption=SubsumptionController()
    def plan(self,grid,goal,w,h,guards):
        r=self.algorithm(grid,(self.x,self.y),goal,w,h,guards)
        p,ne,ct,sr=r;self.total_nodes_explored+=ne;self.total_compute_time+=ct;self.explored_cells.update(sr)
        if p: self.path=p[1:];self.path_index=0
        else: self.path=[];self.path_index=0
        self.needs_replan=False
    def plan_with_danger(self,grid,goal,w,h,dz):
        r=self.algorithm(grid,(self.x,self.y),goal,w,h,dz)
        p,ne,ct,sr=r;self.total_nodes_explored+=ne;self.total_compute_time+=ct;self.explored_cells.update(sr)
        if p: self.path=p[1:];self.path_index=0
        else: self.path=[];self.path_index=0
        self.needs_replan=False;self.predictive_replan_count+=1
    def step_subsumption(self,gs,treasure):
        action,layer=self.subsumption.decide(self,gs)
        if action is None: self.needs_replan=True; return False
        if layer=="emergency_evade":
            if action and isinstance(action,tuple) and len(action)==2:
                self.x,self.y=action;self.total_steps+=1;self.explored_cells.add((self.x,self.y));self.evade_count+=1
                if (self.x,self.y)==treasure: self.found_treasure=True
                return True
        elif layer=="predictive_replan":
            if isinstance(action,tuple) and action[0]=="predictive_replan":
                self.plan_with_danger(gs["grid"],treasure,gs["width"],gs["height"],action[1])
                self.replan_count+=1
            else: self.needs_replan=True;self.replan_count+=1
            return False
        elif layer=="follow_path":
            if action and action not in gs["guard_positions"]:
                self.x,self.y=action;self.path_index+=1;self.total_steps+=1;self.explored_cells.add((self.x,self.y))
                if (self.x,self.y)==treasure: self.found_treasure=True
                return True
            else: self.needs_replan=True;self.replan_count+=1; return False
        elif layer=="explore":
            if action and isinstance(action,tuple):
                self.x,self.y=action;self.total_steps+=1;self.explored_cells.add((self.x,self.y));self.needs_replan=True
                if (self.x,self.y)==treasure: self.found_treasure=True
                return True
        return False
    def get_pos(self): return (self.x,self.y)
    def get_metrics(self):
        return {"algorithm":self.algorithm_name,"path_length":self.total_steps,
                "nodes_explored":self.total_nodes_explored,"compute_time":self.total_compute_time,
                "replan_count":self.replan_count,"predictive_replans":self.predictive_replan_count,
                "evade_count":self.evade_count,"found_treasure":self.found_treasure}

class Game:
    def __init__(self,algorithm="A*",wall_density=0.25,num_guards=2,seed=None,visual=True,max_steps=500):
        self.algorithm=algorithm;self.wall_density=wall_density;self.num_guards_count=num_guards
        self.seed=seed;self.visual=visual;self.max_steps=max_steps;self.width=GRID_WIDTH;self.height=GRID_HEIGHT
        self.grid,self.start,self.treasure=generate_map(self.width,self.height,wall_density,seed)
        self.guards=place_guards(self.grid,self.width,self.height,num_guards,self.start,self.treasure)
        self.agent=Agent(self.start,algorithm)
        self.vision_range=4;self.revealed=set();self._reveal(self.start)
        self.step_count=0;self.game_over=False;self.game_result=None
        self.frame=0;self.agent_direction=(1,0);self.prev_agent_pos=self.start
        if self.visual:
            pygame.init();self.screen=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
            pygame.display.set_caption(f"Misty Moon - {algorithm}");self.clock=pygame.time.Clock()
            self.font=pygame.font.SysFont("consolas",14);self.font_large=pygame.font.SysFont("consolas",22,bold=True)
            from sprites import SpriteCache,ParticleSystem
            self.sprites=SpriteCache(CELL_SIZE);self.particles=ParticleSystem();self.victory_emitted=False
    def _reveal(self,pos):
        px,py=pos
        for dx in range(-self.vision_range,self.vision_range+1):
            for dy in range(-self.vision_range,self.vision_range+1):
                nx,ny=px+dx,py+dy
                if 0<=nx<self.width and 0<=ny<self.height and abs(dx)+abs(dy)<=self.vision_range:
                    self.revealed.add((nx,ny))
    def _guard_pos(self): return set(g.get_pos() for g in self.guards)
    def _game_state(self):
        return {"grid":self.grid,"width":self.width,"height":self.height,
                "guard_positions":self._guard_pos(),"guards":self.guards,"treasure":self.treasure}
    def update(self):
        if self.game_over: return
        gp=self._guard_pos()
        for g in self.guards: g.move(gp-{g.get_pos()})
        gs=self._game_state()
        if self.agent.needs_replan: self.agent.plan(self.grid,self.treasure,self.width,self.height,gs["guard_positions"])
        self.agent.step_subsumption(gs,self.treasure);self._reveal(self.agent.get_pos())
        self.step_count+=1
        if self.agent.found_treasure: self.game_over=True;self.game_result="success"
        elif self.step_count>=self.max_steps: self.game_over=True;self.game_result="failure"
    def draw(self):
        self.screen.fill(COLOR_BG);self.frame+=1
        ax,ay=self.agent.get_pos();px,py=self.prev_agent_pos
        if ax!=px or ay!=py:
            self.agent_direction=(ax-px,ay-py)
            self.particles.emit_footstep(ax*CELL_SIZE+CELL_SIZE//2,ay*CELL_SIZE+CELL_SIZE//2)
        self.prev_agent_pos=(ax,ay)
        for y in range(self.height):
            for x in range(self.width):
                pos=(x*CELL_SIZE,y*CELL_SIZE)
                if (x,y) not in self.revealed: self.screen.blit(self.sprites.get_fog(x,y),pos);continue
                cell=self.grid[y][x]
                if cell==Cell.WALL: self.screen.blit(self.sprites.get_wall(x,y),pos)
                elif cell==Cell.START: self.screen.blit(self.sprites.start_sprite,pos)
                elif cell==Cell.TREASURE:
                    self.screen.blit(self.sprites.get_floor(x,y),pos)
                    self.screen.blit(self.sprites.get_treasure(self.frame),pos)
                    if self.frame%8==0: self.particles.emit_sparkle(x*CELL_SIZE+CELL_SIZE//2,y*CELL_SIZE+CELL_SIZE//2-5,count=2)
                else:
                    if (x,y) in self.agent.explored_cells: self.screen.blit(self.sprites.get_explored_floor(x,y),pos)
                    else: self.screen.blit(self.sprites.get_floor(x,y),pos)
        if self.agent.path:
            for i in range(self.agent.path_index,len(self.agent.path)):
                ppx,ppy=self.agent.path[i]
                if (ppx,ppy) in self.revealed: self.screen.blit(self.sprites.get_path_marker(self.frame+i*3),(ppx*CELL_SIZE,ppy*CELL_SIZE))
        for gp in self._guard_pos():
            if gp in self.revealed:
                gx,gy=gp;self.screen.blit(self.sprites.get_guard(self.frame),(gx*CELL_SIZE,gy*CELL_SIZE))
                if self.frame%12==0: self.particles.emit_danger(gx*CELL_SIZE+CELL_SIZE//2,gy*CELL_SIZE+CELL_SIZE//2)
        self.screen.blit(self.sprites.get_agent(self.frame,self.agent_direction),(ax*CELL_SIZE,ay*CELL_SIZE))
        for y in range(self.height):
            for x in range(self.width):
                if (x,y) in self.revealed:
                    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nx,ny=x+dx,y+dy
                        if 0<=nx<self.width and 0<=ny<self.height and (nx,ny) not in self.revealed:
                            e=pygame.Surface((CELL_SIZE,CELL_SIZE),pygame.SRCALPHA)
                            for i in range(CELL_SIZE//2):
                                a=int(80*(1-i/(CELL_SIZE//2)))
                                if dx==1: pygame.draw.line(e,(8,8,18,a),(CELL_SIZE-1-i,0),(CELL_SIZE-1-i,CELL_SIZE))
                                elif dx==-1: pygame.draw.line(e,(8,8,18,a),(i,0),(i,CELL_SIZE))
                                elif dy==1: pygame.draw.line(e,(8,8,18,a),(0,CELL_SIZE-1-i),(CELL_SIZE,CELL_SIZE-1-i))
                                elif dy==-1: pygame.draw.line(e,(8,8,18,a),(0,i),(CELL_SIZE,i))
                            self.screen.blit(e,(x*CELL_SIZE,y*CELL_SIZE))
        if self.game_over and self.game_result=="success" and not self.victory_emitted:
            self.particles.emit_victory(ax*CELL_SIZE+CELL_SIZE//2,ay*CELL_SIZE+CELL_SIZE//2,count=50);self.victory_emitted=True
        self.particles.update();self.particles.draw(self.screen)
        hud_y=self.height*CELL_SIZE;pygame.draw.rect(self.screen,COLOR_HUD_BG,(0,hud_y,SCREEN_WIDTH,60))
        pygame.draw.line(self.screen,(60,60,100),(0,hud_y),(SCREEN_WIDTH,hud_y),2)
        ln=self.agent.subsumption.active_layer_name
        lc={"emergency_evade":(255,60,60),"predictive_replan":(255,180,50),"follow_path":(80,200,120),"explore":(150,150,200)}.get(ln,(100,100,100))
        for i,(t,c) in enumerate([(f"Algo:{self.algorithm}",COLOR_AGENT),(f"Steps:{self.step_count}/{self.max_steps}",COLOR_TEXT),
            (f"Replan:{self.agent.replan_count}",(255,180,80)),(f"Evade:{self.agent.evade_count}",COLOR_GUARD),(f"Layer:{ln}",lc)]):
            self.screen.blit(self.font.render(t,True,c),(10+i*160,hud_y+8))
        if self.game_over:
            t="TREASURE FOUND!" if self.game_result=="success" else "TIME UP!"
            c=COLOR_TREASURE if self.game_result=="success" else COLOR_GUARD
            s=self.font_large.render(t,True,c);self.screen.blit(s,(SCREEN_WIDTH//2-s.get_width()//2,hud_y+32))
        pygame.display.flip()
    def run_visual(self):
        running=True
        while running:
            for e in pygame.event.get():
                if e.type==pygame.QUIT: running=False
                if e.type==pygame.KEYDOWN:
                    if e.key==pygame.K_ESCAPE: running=False
                    if e.key==pygame.K_SPACE and self.game_over: running=False
            self.update();self.draw();self.clock.tick(FPS)
        pygame.quit();return self.agent.get_metrics()
    def run_headless(self):
        while not self.game_over: self.update()
        return self.agent.get_metrics()

def main():
    import sys
    a="A*";wd=0.25;ng=3
    if len(sys.argv)>1: a=sys.argv[1]
    if len(sys.argv)>2: wd=float(sys.argv[2])
    if len(sys.argv)>3: ng=int(sys.argv[3])
    print(f"Misty Moon Treasure Hunt\n  Algorithm: {a}\n  Walls: {wd}\n  Guards: {ng}")
    print(f"  Architecture: Subsumption (emergency_evade > predictive_replan > follow_path > explore)")
    g=Game(algorithm=a,wall_density=wd,num_guards=ng,visual=True,max_steps=500)
    m=g.run_visual();print(f"\nResults: {m}")

if __name__=="__main__": main()
