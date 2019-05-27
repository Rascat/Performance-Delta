from git import Repo
import subprocess
from pathlib import Path

home = str(Path.home())
peass_root = home + "/Code/peassquickstart"
path_to_pom = peass_root + "/pom.xml"

def main():
    repo = Repo(peass_root)
    if repo.is_dirty():
        print(repo.untracked_files)
    
    commit_list = list(repo.iter_commits('master')) # list of all commits in branch master

    for commit in commit_list:
        repo.git.checkout(commit.hexsha)
        run_mvn_test(path_to_pom)


def run_mvn_test(path_to_pom: str):
    subprocess.run(["mvn test -f " + path_to_pom], shell = True)

    
    

    

    
if __name__ == "__main__": main()
