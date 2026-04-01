import pandas as pd
import matplotlib.pyplot as plt
import os

class logger:
    def __init__(self):
        # This list will grow with every call to record()
        self.raw_data = []

    def record(self, tokens, runtime, length):
        """
        Appends new data to the existing in-memory list.
        """
        entry = {
            'tokens': tokens,
            'runtime': runtime,
            'length': length,
            'tps': tokens / runtime if runtime > 0 else 0
        }
        self.raw_data.append(entry)
        print(f"Logged run {len(self.raw_data)}: {tokens} tokens processed.")

    def get_df(self):
        """
        Converts the accumulated list of dictionaries into a Pandas DataFrame.
        """
        return pd.DataFrame(self.raw_data)

    def save_plots(self, filename="performance_results.png"):
        df = self.get_df()
        if df.empty:
            return

        # 1. Create the figure (same as before)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        ax1.scatter(df['length'], df['tokens'], alpha=0.6)
        ax1.set_title('Prompt Length vs. Tokens')
        ax1.set_xlabel('Prompt Length (Characters/Words)')
        ax1.set_ylabel('Token Count')
        
        ax2.scatter(df['length'], df['runtime'], color='orange', alpha=0.6)
        ax2.set_title('Prompt Length vs. Runtime')
        ax2.set_xlabel('Prompt Length (Characters/Words)')
        ax2.set_ylabel('Runtime (Seconds)')

        # 2. Save the file
        # You can use .png, .jpg, .pdf, or .svg
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f" Plot saved as {filename}")
        
        # 3. Close the plot to free up memory
        plt.close(fig)