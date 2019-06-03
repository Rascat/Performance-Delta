import analyzer
import sys
import utils
import runner

def main():
    if len(sys.argv) < 3:
        print("Please provide path to mvn repository and number of commits")
        exit(1)
    
    project_root = sys.argv[1]
    commit_count = int(sys.argv[2])

    # runner.run(project_root, commit_count)
    log_dir = utils.get_log_dir(project_root)
    analyzer.analyze(log_dir)


# argv[1]: path to maven project
# argv[2]: number of commits to iterate, starting from HEAD
if __name__ == "__main__": main()
