import threading
import time
import signal
import sys

class Parent:
    def __init__(self, name="Parent"):
        
        self.name = name
        self._running = False
        self._thread = None
        self._completed = threading.Event()
        # # if you need child also to have its own thread aside the parent, uncomment below 
        # self._child_thread = None 
        self._exit_flag = threading.Event()  # Flag to signal exit for all threads
        
        # Set up signal handler for graceful exit
        self._original_sigint_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, sig, frame):
        """Internal signal handler for Ctrl+C"""
        print("\nCtrl+C detected! Shutting down gracefully...")
        self.stop()
        time.sleep(0.5)  # Small delay to allow threads to respond
        # Restore original handler and re-raise the signal
        signal.signal(signal.SIGINT, self._original_sigint_handler)
        sys.exit(0)
    
    def runUntilStopped(self):
        print(f"{self.name} started running")
        try:
            self._running = True
            while self._running and not self._exit_flag.is_set():
                try:
                    # Use a timeout to allow checking for exit flag
                    char = input(f'[{self.name}] enter details. /exit to quit: ')
                    if char == '/exit':
                        break
                    print(char)
                except KeyboardInterrupt:
                    print(f"\n{self.name} process interrupted")
                    break
        except Exception as e:
            print(f"Error in {self.name}: {e}")
        finally:
            print(f"{self.name} finished running")
            self._running = False
            self._completed.set()  # Signal that parent has completed
        
    def start(self):
        """Start the parent process"""
        if self._exit_flag.is_set():
            self._exit_flag.clear()
        self._running = True
        self._thread = threading.Thread(target=self.runUntilStopped)
        self._thread.daemon = True  # Make threads daemon to auto-exit on main thread exit
        self._thread.start()
    
    def stop(self):
        """Stop all threads gracefully"""
        self._exit_flag.set()
        self._running = False
        self._completed.set()  # Set completion event to unblock waiting threads
        
    def join(self, timeout=None):
        """Wait for this parent to complete its execution"""
        try:
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout)
            
            
            # if you need child also to have its own thread aside the parent, uncomment below 
            # if self._child_thread and self._child_thread.is_alive():
            #     self._child_thread.join(timeout)
            
        except KeyboardInterrupt:
            print("\nJoin interrupted. Stopping threads...")
            self.stop()
    
    def wait_for_completion(self):
        """Wait for the completion event to be set"""
        while not self._completed.is_set() and not self._exit_flag.is_set():
            # Wait with timeout to check for exit flag
            self._completed.wait(0.5)
        
    def parentStart(self):
        """Start the parent and wait for it to complete before continuing with child execution"""
        # Start parent
        self.start()
       
        # if you need child also to have its own thread aside the parent, uncomment below 
        # Create a thread to wait for parent completion and then continue with child execution
        # def wait_and_continue():
        #     try:
        #         print(f"Waiting for parent process to finish...")
        #         self.wait_for_completion()
                
        #         # Check if we should exit
        #         if self._exit_flag.is_set():
        #             return
                
        #         print(f"Parent process finished, continuing with child execution")
        #         # Here the child would continue its execution after parent is done
        #         self._running = True
        #         while self._running and not self._exit_flag.is_set():
        #             try:
        #                 char = input(f'[Child] enter details. /exit to quit: ')
        #                 if char == '/exit':
        #                     break
        #                 print(char)
        #             except KeyboardInterrupt:
        #                 print("\nChild process interrupted")
        #                 break
        #         print("Child execution finished")
        #     except Exception as e:
        #         print(f"Error in child thread: {e}")
            
        # self._child_thread = threading.Thread(target=wait_and_continue)
        # self._child_thread.daemon = True  # Make daemon to auto-exit on main thread exit
        # self._child_thread.start()
        # return self
    
    def cleanup(self):
        """Clean up resources and restore original signal handlers"""
        self.stop()
        # Restore original signal handler
        signal.signal(signal.SIGINT, self._original_sigint_handler)


# Example of the minimal client code needed in a real application:
if __name__ == "__main__":
    # This is all you need to write in the child code:
    parent = Parent()  # Line 1
    parent.parentStart()  # Line 2
    
    # Optionally, you can wait for completion
    parent.join()
    
    # Always good to cleanup at the end of your program
    parent.cleanup()
        
        
