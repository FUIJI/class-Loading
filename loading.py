from threading import Thread, Lock
from time import sleep

class BaseLoader:
    """
    Base class for console loaders.
    Provides the basic structure and methods to start, animate, and stop the loader.
    """

    ANIMATION_STEPS = []
    VALID_POSITIONS = ["front", "end"]
    
    def __init__(self, desc: str="Loading...", end: str="Done!", timeout: float=0.1, position:str ="front") -> None:
        """
        Initialize the loader with given parameters.
        
        Args:
            desc (str): The description of the loader.
            end (str): Message to display after the animation ends.
            timeout (float): Duration (in seconds) to wait between animation frames.
            position (str): Position of the animation relative to the description. Either "front" or "end".
        """
        
        self._config = {
            "desc": desc,
            "end": end,
            "timeout": timeout,
            "position": position
        }
        self._done = False
        self._lock = Lock() # Introduce a lock for thread safety
        
        if self._config["position"] not in self.VALID_POSITIONS:
            raise ValueError(f"Invalid position: {self._config['position']}. Choose either 'front' or 'end'.")
        if not self.ANIMATION_STEPS:
            raise ValueError("ANIMATION_STEPS must be defined in derived classes and cannot be empty.")


    def __enter__(self) -> None:
        """
        Start the animation thread when the context is entered.

        This method initializes and starts a daemonized thread that runs 
        the `_animate` method. By setting it as a daemon, it ensures the thread 
        will automatically exit when the main program finishes. The `_done` flag 
        is set to False, indicating the animation is active.
        """
        # Ensure thread-safety when modifying the _done flag.
        with self._lock:  
            self._done = False
            
        # Initialize and start the daemonized animation thread.
        self._thread = Thread(target=self._animate, daemon=True)
        self._thread.start()
               
            
    def _animate(self) -> None:
        """Handles the core animation logic for the loader."""
        
        # Initialize the step counter for animation frames
        step_count = 0

        try:
            while True:
                # Using a lock to safely check the _done flag
                with self._lock:
                    if self._done:
                        break

                # Check the position configuration to determine the order of the animation and description.
                prefix, suffix = (
                    (self.ANIMATION_STEPS[step_count], self._config['desc']) 
                    if self._config["position"] == "front" 
                    else (self._config['desc'], self.ANIMATION_STEPS[step_count])
                )
                print(f"\r{prefix} {suffix}", flush=True, end="")

                # Pause the execution for a specified duration (timeout) before the next animation frame
                sleep(self._config["timeout"])
                
                # Increment the step counter, and wrap-around if it exceeds the total number of animation steps
                step_count = (step_count + 1) % len(self.ANIMATION_STEPS)
                
        except KeyboardInterrupt:
            pass  # Allow the user to interrupt the animation
        except Exception as e:
            print(f"Animation thread error: {e}")



    def __exit__(self, *args) -> None:
        """
        Gracefully stop the animation thread when the context is exited.

        This method ensures thread-safety when updating the `_done` flag.
        Additionally, it clears any ongoing animation from the console and prints 
        the configured end message. It waits for the animation thread to finish 
        before exiting to ensure no lingering threads.
        """
        # Safely set the _done flag to stop the animation thread.
        with self._lock:  
            self._done = True
            
        # Clear the ongoing animation from the console.
        print("\r" + " " * (len(self._config["desc"]) + len(self.ANIMATION_STEPS[0]) + 1), end="", flush=True)
        
        # Print the end message
        print(f"\r{self._config['end']}", flush=True)
        
        # Wait for the animation thread to finish
        self._thread.join()
        

class LineLoader(BaseLoader):
    ANIMATION_STEPS = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]

class GrowthLoader(BaseLoader):
    ANIMATION_STEPS = ["·", "•", "●", "•", "·"]

class CircleLoader(BaseLoader):
    ANIMATION_STEPS = ["◓", "◑", "◒", "◐"]

class PulseLoader(BaseLoader):
    ANIMATION_STEPS = ["•", "○", "•", "·", "●", "·"]

class BounceLoader(BaseLoader):
    ANIMATION_STEPS = ["<• ", "<•>", " •>", " • "]

class DotLoader(BaseLoader):
    ANIMATION_STEPS = ["·", "•", "••", "•••", "••••", "•••", "••", "•"]

class BartLoader(BaseLoader):
    ANIMATION_STEPS = ["_", "▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]


# Testing the refactored loaders
if __name__ == "__main__":
    with LineLoader("Line loading..."):
        for _ in range(15):
            sleep(0.25)


    loader = BartLoader("Loading Bounce loader object...", "Super fast!", timeout=0.15, position="end")
    with loader:
        for _ in range(15):
            sleep(0.25)