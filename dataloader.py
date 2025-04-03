from pandas import read_excel
from ast import literal_eval

class LensDataLoader:
    def __init__(self, file_path, lens_count=2):
        self.file_path = file_path
        self.lens_count = lens_count
        self.lens_combinations = []

    def load_data(self):
        """加载镜片数据并解析为组合"""
        try:
            df = read_excel(self.file_path)
            for _, row in df.iterrows():
                lenses = []
                for i in range(1, self.lens_count + 1):
                    lens = literal_eval(row[f"镜片{i}"])  # 将字符串解析为元组
                    lenses.append(lens)
                self.lens_combinations.append(tuple(lenses))
        except Exception as e:
            print(f"加载数据时出错: {e}")

    def get_combinations(self):
        """返回镜片组合"""
        return self.lens_combinations

    def get_total_combinations(self):
        """返回镜片组合的总数量"""
        return len(self.lens_combinations)
