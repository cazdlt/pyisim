import time

def TicTocGenerator():
    # Generator that returns time differences
    ti = 0           # initial time
    tf = time.time() # final time
    while True:
        ti = tf
        tf = time.time()
        yield tf-ti # returns the time difference

TicToc = TicTocGenerator()

def toc(mensaje="Tiempo transcurrido: ",imprimir=True):
    intervalo = next(TicToc)
    if imprimir:
        print( f"{mensaje}: {intervalo:.3f}s")

def tic():
    toc(imprimir=False)

if __name__ == "__main__":
    tic()
    time.sleep(1)
    toc()
    time.sleep(1)
    toc("Tiempo dormido")