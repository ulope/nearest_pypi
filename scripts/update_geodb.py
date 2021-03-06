import os
import subprocess
from config import Config


class Command(object):
    def run(self):

        geodb_file_v4 = "{}.gz".format(Config.GEOIP_PATH_V4)
        geodb_file_v6 = "{}.gz".format(Config.GEOIP_PATH_V6)

        with open(os.devnull, "w") as devnull:
            subprocess.call(
                [
                    'wget',
                    '-O', geodb_file_v4,
                    Config.GEOIP_DB_URL_IPV4,
                ],
                stdout=devnull,
                stderr=devnull
            )
            subprocess.call(["gunzip", "-f", geodb_file_v4])

            subprocess.call(
                [
                    'wget',
                    '-O', geodb_file_v6,
                    Config.GEOIP_DB_URL_IPV6,
                ],
                stdout=devnull,
                stderr=devnull
            )
            subprocess.call(["gunzip", "-f", geodb_file_v6])

if __name__ == "__main__":
    Command().run()
