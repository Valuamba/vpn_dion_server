
class ServerStatistic:

    def __init__(self, network_upload, network_download, network_upload_speed, network_download_speed, total, ram, cpu):
        self.networkUpload_b = network_upload
        self.network_download_b = network_download
        self.network_upload_speed_b = network_upload_speed
        self.network_download_speed_b = network_download_speed
        self.total_b = total
        self.ram = ram
        self.cpu = cpu
