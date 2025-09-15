import sys
from astropy.time import Time

def utc_to_gps(utc_str):
    """
    Convert UTC date string (YYYY-MM-DD) at 12:00 to GPS seconds.
    """
    # Add time 12:00 explicitly
    t = Time(f"{utc_str} 12:00:00", scale="utc")
    # Convert to GPS scale
    return int(t.gps)

def main():
    if len(sys.argv) < 3:
        print("Warning, usage: python script.py <start_date YYYY-MM-DD> <stop_date YYYY-MM-DD> [filename]")
        #sys.exit(1)
        start_str = "2025-09-12"
        stop_str  = "2025-09-29"
    else:

        start_str = sys.argv[1]  # "2025-07-16"
        stop_str  = sys.argv[2]  # "2025-08-03"
    
    filename  = "startstoptimes.inc"

    gps_start = utc_to_gps(start_str)
    gps_stop  = utc_to_gps(stop_str)

    # Read file
    with open(filename, "r") as f:
        lines = f.readlines()

    # Rewrite file
    with open(filename, "w") as f:
        for line in lines:
            if line.strip().startswith("double gpsStart=") or line.strip().startswith("double gpsStop="):
                f.write("//" + line)
            else:
                f.write(line)

        # Append new block
        f.write("\n")
        f.write(f"// {start_str} 12:00 - {stop_str} 12:00\n")
        f.write(f"double gpsStart={gps_start};\n")
        f.write(f"double gpsStop={gps_stop};\n")

    print(f"Updated {filename}")
    print(f"gpsStart={gps_start}, gpsStop={gps_stop}")

if __name__ == "__main__":
    main()
