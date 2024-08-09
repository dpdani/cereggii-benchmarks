import subprocess

from .config import config


class Growt:
    block_size = 8192
    installation_dir = config["growt_installation_dir"]
    assert installation_dir.is_dir()

    def run_command(self, command: str, wall_clock_time_col_name: str) -> float:
        command = f"./{self.installation_dir}/build/{command}"
        print(f"    - {command}")
        p = subprocess.Popen(
            command,
            shell=True,
            cwd=self.installation_dir,
            stdout=subprocess.PIPE,
        )
        p.wait()
        return self.parse_output(
            p.stdout.read().decode(),
            wall_clock_time_col_name,
        )

    @staticmethod
    def parse_output(output: str, wall_clock_time_col_name: str) -> float:
        lines = output.splitlines()
        line_1 = lines[0]
        columns = list(filter(None, line_1.split(" ")))
        assert columns[-1] == "migration_table<base_table<simple_slot,lmap,lprob>,w_user,e_sync_new>"
        assert wall_clock_time_col_name in columns
        line_2 = lines[1]
        values = list(filter(None, line_2.split(" ")))
        assert len(values) == len(columns) - 1
        return float(values[columns.index(wall_clock_time_col_name)]) / 1_000  # output is in ms

    def aggregation(self, threads: int, keys_count: int, min_size: int, skew: float):
        return self.run_command(
            (
                f"agg/agg_full_usGrowT "
                f" -it {1}"
                f" -p {threads}"
                f" -n {keys_count}"
                f" -c {min_size}"
                f" -con {skew}"
            ),
            "t_aggreg"
        )

    def delete(self, threads: int, keys_count: int, min_size: int, window_size: int):
        return self.run_command(
            (
                f"del/del_full_usGrowT "
                f" -it {1}"
                f" -p {threads}"
                f" -n {keys_count}"
                f" -ws {window_size}"
                f" -c {min_size}"
            ),
            "t_del"
        )

    def insert(self, threads: int, keys_count: int, min_size: int):
        return self.run_command(
            (
                f"ins/ins_full_usGrowT "
                f" -it {1}"
                f" -p {threads}"
                f" -n {keys_count}"
                f" -c {min_size}"
            ),
            "t_ins"
        )

    def lookup_contention(self, threads: int, keys_count: int, min_size: int, skew: float):
        return self.run_command(
            (
                f"con/con_full_usGrowT "
                f" -it {1}"
                f" -p {threads}"
                f" -n {keys_count}"
                f" -c {min_size}"
                f" -con {skew}"
            ),
            "t_find_c"
        )

    def lookup_fail(self, threads: int, keys_count: int, min_size: int):
        return self.run_command(
            (
                f"ins/ins_full_usGrowT "
                f" -it {1}"
                f" -p {threads}"
                f" -n {keys_count}"
                f" -c {min_size}"
            ),
            "t_find_-"
        )

    def lookup_succ(self, threads: int, keys_count: int, min_size: int):
        return self.run_command(
            (
                f"ins/ins_full_usGrowT "
                f" -it {1}"
                f" -p {threads}"
                f" -n {keys_count}"
                f" -c {min_size}"
            ),
            "t_find_+"
        )

    def mix(self, threads: int, keys_count: int, min_size: int, wp: float) -> float:
        pre = self.block_size * threads
        return self.run_command(
            (
                f"mix/mix_full_usGrowT"
                f" -it {1}"
                f" -p {threads}"
                f" -n {keys_count}"
                f" -c {min_size}"
                f" -pre {pre}"
                f" -win {pre}"
                f" -wperc {wp}"
            ),
            "t_mix",
        )

    def update_contention(self, threads: int, keys_count: int, min_size: int, skew: float):
        return self.run_command(
            (
                f"con/con_full_usGrowT"
                f" -it {1}"
                f" -p {threads}"
                f" -n {keys_count}"
                f" -c {min_size}"
                f" -con {skew}"
            ),
            "t_updt_c"
        )
