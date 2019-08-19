from os import walk
from multiprocessing.dummy import Pool

class Find():

    # Search a keyword in modules code (comments included)

    def search(self, word):
        """Search a given word into the module directory
        
        Args:
            word (str): word to search
        
        Returns:
            [str]: List of string found
        """
        self.search_key = word
        my_list = []
        for path, dirs, files in walk('modules'):
            for f in files:
                if not "__" in path+'/'+f and not f.startswith("_"):
                    my_list.append(path+'/'+f)
        pool = Pool(2)
        results = pool.map(self.is_in_module, my_list)
        pool.close()
        pool.join()
        return self._clean_results(results)

    def is_in_module(self, arg):
        try:
            fr = open(arg, 'r')
            if self.search_key in fr.read().lower():
                return arg.replace(".py","").replace("modules/","")
            fr.close()
        except:
            return None

    def _clean_results(self, results):
        while None in results:
            results.remove(None)
        return results
         