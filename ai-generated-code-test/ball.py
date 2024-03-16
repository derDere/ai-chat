"""A bouncing ball animation
"""


import tkinter
import random
import time


class Ball:
  """A ball object
  """
  def __init__(self, canvas:tkinter.Canvas, color:str) -> None:
    self.canvas = canvas
    self.id = canvas.create_oval(10, 10, 25, 25, fill=color)
    self.canvas.move(self.id, 245, 100) # type: ignore
    starts = [-3, -2, -1, 1, 2, 3]
    random.shuffle(starts)
    self.x = starts[0]
    self.y = -3
    self.canvas_height = self.canvas.winfo_height()
    self.canvas_width = self.canvas.winfo_width()

  def draw(self) -> None:
    """Draws the ball
    """
    self.canvas.move(self.id, self.x, self.y) # type: ignore
    pos = self.canvas.coords(self.id)
    if pos[1] <= 0:
      self.y = 3
    if pos[3] >= self.canvas_height:
      self.y = -3
    if pos[0] <= 0:
      self.x = 3
    if pos[2] >= self.canvas_width:
      self.x = -3


def main() -> None:
  """Main function
  """
  # create the canvas
  tk = tkinter.Tk()
  tk.title("Bouncing Ball Animation")
  #tk.resizable(0, 0)
  #tk.wm_attributes("-topmost", 1)
  canvas = tkinter.Canvas(tk, width=500, height=500, bd=0, highlightthickness=0)
  canvas.pack()
  tk.update()

  # create the objects
  ball = Ball(canvas, 'red')

  # animate the ball
  while True:
    ball.draw()
    tk.update_idletasks()
    tk.update()
    time.sleep(0.01)

  tk.mainloop()


if __name__ == "__main__":
  main()
