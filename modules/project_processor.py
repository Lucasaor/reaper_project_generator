import pandas as pd
from uuid import uuid4
import re
from loguru import logger
from datetime import datetime


class ProjectProcessor:
    """
    A class to process Reaper project files and manage markers and regions.
    Attributes:
        project_df (pd.DataFrame): DataFrame to store project data.
        df_to_export (pd.DataFrame): DataFrame to store data to be exported.
        original_project_name (str): Original project name.
        rpp_file (str): Content of the original Reaper project file.
        new_rpp_file (str): Content of the new Reaper project file.
        song_list (list): List of available songs in the project.
        current_setlist (list): List of songs in the current setlist.
        features_order (list): Order of features in the DataFrame.
        constant_features (dict): Constant features for markers.
    Methods:
        load_project(reaper_project: str) -> None:
            Loads a Reaper project file and processes its markers and regions.
        extract_available_songs_in_project() -> None:
            Extracts available songs from the project, excluding regions with color 0.
        set_setlist(setlist: list[str]) -> None:
            Sets the current setlist with the given list of songs.
        remove_all_markers_from_project() -> None:
            Removes all markers from the project.
        create_markers_from_setlist() -> None:
            Creates markers for the current setlist and updates the DataFrame.
        create_new_rpp_file() -> None:
            Creates a new Reaper project file with the updated markers and regions.
    """
    def __init__(self):
        self.project_df = pd.DataFrame()
        self.df_to_export = pd.DataFrame()
        self.original_project_name = None
        self.rpp_file = ''
        self.new_rpp_file = ''
        self.song_list = []
        self.current_setlist = []
        self.features_order = ['tag', 'number', 'start_position', 'name', 'is_region', 'color','unkown_0', 'unknown_1', 'uuid', 'unkown_3']
        self.constant_features = {
            'tag': 'MARKER',
            'unkown_0': '1',
            'unknown_1': 'R',
            'unkown_3': '0'
        }
    
    def load_project(self, reaper_project_content: bytes|str, file_name = None) -> None:
        """
        Load a Reaper project file content and process its markers and regions.
        This method reads the content of a Reaper project file, extracts marker and region data,
        processes the data into a pandas DataFrame, and performs various cleaning
        and transformation steps. The resulting DataFrame is stored in the 
        `self.project_df` attribute.
        Args:
            reaper_project_content (str): The content of the Reaper project file.
        Returns:
            None
        """
        
        logger.info("Loading Reaper project from content")

        self.original_project_name = file_name
        if isinstance(reaper_project_content, bytes):
            reaper_project_content = reaper_project_content.decode('utf-8')
        
        self.rpp_file = reaper_project_content

        # Find lines that start with "MARKER"
        region_marker_data = re.findall(r'MARKER.*', reaper_project_content)
        region_marker_data = [re.split(r' (?=(?:[^"]*"[^"]*")*[^"]*$)', x) for x in region_marker_data]

        # Create a DataFrame from the list of lists
        df = pd.DataFrame(region_marker_data, columns=['tag', 'number', 'start_position', 'name', 'is_region', 'color', 'unkown_0', 'unknown_1', 'uuid', 'unkown_3'])

        # Remove the double quotes from the name column
        df['name'] = df['name'].str.replace('"', '')

        # Remove curly brackets from the uuid column
        df['uuid'] = df['uuid'].str.replace('{', '')
        df['uuid'] = df['uuid'].str.replace('}', '')

        # Create end position column for regions
        df['end_position'] = df['start_position'].shift(-1)

        # Set the end position for markers (not regions) as None
        df.loc[df['is_region'] == '0', 'end_position'] = None

        # Drop regions where name is ""
        df = df[df['name'] != '']

        # Drop unknown columns
        df = df.drop(columns=['unkown_0', 'unknown_1', 'unkown_3'])

        self.project_df = df
        logger.info(f"Reaper project loaded with {len(df)} markers and regions")
        self.remove_all_markers_from_project()
        logger.info(f"Markers removed from project. {len(self.project_df)} regions remaining")
        self.extract_available_songs_in_project()
        
    
    def extract_available_songs_in_project(self)->None:
        """
        Extracts the available songs in the project, excluding regions with color 0.

        This method processes the project DataFrame to filter out regions that are not applicable
        (regions with color 0) and extracts the unique song names from the remaining regions.
        The extracted song names are stored in the `song_list` attribute.

        Returns:
            None

        Logs:
            - Info: When starting the extraction process.
            - Error: If no project is loaded (i.e., the project DataFrame is empty).
            - Info: The number of songs found in the project.
        """
        logger.info("Extracting available songs in project (excluding not applicable regions with color 0)")
        if self.project_df.empty:
            logger.error("No project loaded")
            return

        df = self.project_df
        # get only the regions in df
        df = df[df['is_region'] == '1']

        # get the unique song names
        self.song_list:list = df.query("color != '0'")['name'].unique().tolist()
        self.song_list.sort()
        logger.info(f"{len(self.song_list)} songs found in project")

    def get_song_list(self)->list[str]:
        """
        Returns the list of available songs in the project.

        This method returns the list of available songs in the project, which is extracted
        from the project DataFrame. If no project is loaded (i.e., the project DataFrame is empty),
        an error is logged and an empty list is returned.

        Returns:
            list[str]: A list of available songs in the project.
        """
        return self.song_list
    
    def get_setlist(self)->list[str]:
        """
        Returns the current setlist for the project.

        This method returns the current setlist for the project, which is stored in the `current_setlist`
        attribute. If no setlist is set (i.e., the `current_setlist` attribute is None), an error is logged
        and an empty list is returned.

        Returns:
            list[str]: A list of songs in the current setlist.
        """
        return self.current_setlist

    def set_setlist(self, setlist:list[str])->None:
        """
        Sets the current setlist for the project.

        This method takes a list of song names and sets it as the current setlist
        if all songs are present in the project's song list. If any song in the 
        setlist is not found in the project's song list, an error is logged and 
        the setlist is not updated.

        Args:
            setlist (list[str]): A list of song names to be set as the current setlist.

        Returns:
            None
        """
        for song in setlist:
            if song not in self.song_list:
                logger.error(f"Song {song} not in project")
                return

        self.current_setlist = setlist
        logger.info(f"Setlist created with {len(setlist)} songs")
        
    def remove_all_markers_from_project(self)->None:
        """
        Removes all markers from the project.

        This method filters out all rows in the project's DataFrame where the 'is_region' 
        column is '0', effectively removing all markers. If the project's DataFrame is 
        empty, an error is logged and the method returns without making any changes.

        Returns:
            None
        """
        if self.project_df.empty:
            logger.error("No project loaded")
            return
        logger.info("Removing all markers from project")
        df = self.project_df
        df = df[df['is_region'] != '0']
        self.project_df = df
        
    def create_markers_from_setlist(self):
        """
        Creates markers for each song in the current setlist and appends them to the project dataframe.
        This method processes the current setlist and generates markers for each song, including skip markers.
        The markers are then concatenated to the existing project dataframe and sorted by start position.
        The generated markers include:
        - Tag
        - Number
        - Start position
        - End position (None)
        - Name
        - Is region (0)
        - Color (0)
        - UUID
        - Additional constant features
        The resulting dataframe is stored in `self.df_to_export`.
        Parameters:
        None
        Returns:
        None
        """

        marker_map = {
            1: 40161,
            2: 40162,
            3: 40163,
            4: 40164,
            5: 40165,
            6: 40166,
            7: 40167,
            8: 40168,
            9: 40169,
            10: 40160,
            11: 41251,
            12: 41252,
            13: 41253,
            14: 41254,
            15: 41255,
            16: 41256,
            17: 41257,
            18: 41258,
            19: 41259,
            20: 41260,
            21: 41261,
            22: 41262,
            23: 41263,
            24: 41264,
            25: 41265,
            26: 41266,
            27: 41267,
            28: 41268,
            29: 41269,
            30: 41270
        }

        df = self.project_df
        setlist = self.current_setlist

        logger.info(f"Creating markers for {len(setlist)} songs")
        new_markers_df = pd.DataFrame({
            'tag': [self.constant_features['tag']],
            'number': ['99'],
            'start_position': ['1'],
            'end_position': [None],
            'name': ['!40161'],
            'is_region': ['0'],
            'color': ['0'],
            'unkown_0': [self.constant_features['unkown_0']],
            'unknown_1': [self.constant_features['unknown_1']],
            'uuid': [str(uuid4()).upper()],
            'unkown_3': [self.constant_features['unkown_3']]
        })


        for number,song in enumerate(setlist):
            uuid = str(uuid4()).upper()
            start_position = df.loc[df['name'] == song, 'start_position'].values[0]
            new_markers_df = pd.concat([new_markers_df,pd.DataFrame({
                                                    'tag': [self.constant_features['tag']],
                                                    'number': [str(number+1)],
                                                    'start_position': [start_position],
                                                    'end_position': [None],
                                                    'name': [song],
                                                    'is_region': ['0'],
                                                    'color': ['0'],
                                                    'unkown_0': [self.constant_features['unkown_0']],
                                                    'unknown_1': [self.constant_features['unknown_1']],
                                                    'uuid': [uuid],
                                                    'unkown_3': [self.constant_features['unkown_3']]
                                                    })], ignore_index=True)
            
            # creating skip markers
            uuid = str(uuid4()).upper()
            start_position = df.loc[df['name'] == song, 'end_position'].values[0]
            start_position = str(int(float(start_position) -1))
            if number < len(setlist) - 1:
                new_markers_df = pd.concat([new_markers_df,pd.DataFrame({
                                                        'tag': [self.constant_features['tag']],
                                                        'number': [str(len(setlist)+number+1)],
                                                        'start_position': [start_position],
                                                        'end_position': [None],
                                                        'name': ['!'+str(marker_map[number+2])],
                                                        'is_region': ['0'],
                                                        'color': ['0'],
                                                        'unkown_0': [self.constant_features['unkown_0']],
                                                        'unknown_1': [self.constant_features['unknown_1']],
                                                        'uuid': [uuid],
                                                        'unkown_3': [self.constant_features['unkown_3']]
                                                        })], ignore_index=True)
            
            else:
                new_markers_df = pd.concat([new_markers_df,pd.DataFrame({
                                                        'tag': [self.constant_features['tag']],
                                                        'number': [str(len(setlist)+number+1)],
                                                        'start_position': [start_position],
                                                        'end_position': [None],
                                                        'name': ['!'+str(1016+number)],
                                                        'is_region': ['0'],
                                                        'color': ['0'],
                                                        'unkown_0': [self.constant_features['unkown_0']],
                                                        'unknown_1': [self.constant_features['unknown_1']],
                                                        'uuid': [uuid],
                                                        'unkown_3': [self.constant_features['unkown_3']]
                                                        })], ignore_index=True)


        new_df = pd.concat([df,new_markers_df], ignore_index=True)
        new_df.sort_values(by='start_position', inplace=True)
        new_df = new_df[self.features_order + ['end_position']]
        self.df_to_export = new_df
    
    def create_new_rpp_file(self)-> tuple[str,str]:
        """
        Creates a new RPP (Reaper Project) file by processing and modifying the existing RPP file content.
        This method performs the following steps:
        1. Initializes an empty string for the output text.
        2. Fills NaN values in the DataFrame `df_to_export` with empty strings.
        3. Updates the DataFrame with constant features.
        4. Sets the 'tag' column to '  MARKER' for all rows except the first.
        5. Iterates over the DataFrame rows and constructs the output text based on the specified features order.
        6. Adds additional marker lines if the row represents a region.
        7. Finds the position of the first "MARKER" in the existing RPP file.
        8. Removes all lines starting with "MARKER" from the existing RPP file.
        9. Inserts the constructed output text at the position of the first "MARKER".
        10. Removes leading spaces from lines before the <PROJBAY> section.
        11. Updates the `new_rpp_file` attribute with the modified RPP file content.
        """

        output_text = ""
        new_df = self.df_to_export

        new_df.fillna('', inplace=True)
        for key, value in self.constant_features.items():
            new_df[key] = value

        new_df.loc[1:,'tag'] = '  MARKER'

        for _, row in new_df.iterrows():
            for feature in self.features_order:
                if feature == 'name' and ' ' in row[feature]:
                    output_text += f'"{row[feature]}" '
                elif feature == 'unkown_3':
                    output_text += f"{row[feature]}"
                else:
                    output_text += f"{row[feature]} "
            output_text += "\n"
            if row['is_region'] == '1':
                output_text += f'  MARKER {row['number']} {row['end_position']} \"\" 1\n'

        # Get the position of the first "MARKER" in rpp_file
        first_marker_pos = self.rpp_file.find('MARKER')

        # Remove all lines that start with "MARKER" from rpp_file
        rpp_file_cleaned = re.sub(r'MARKER.*\n', '', self.rpp_file)

        # Insert output_text in the position of the first "MARKER"
        new_rpp_file = rpp_file_cleaned[:first_marker_pos] + output_text + rpp_file_cleaned[first_marker_pos:]

        projbay_pos = new_rpp_file.find('<PROJBAY')
        # Remove all spaces between the beginning of the line and projbay_pos
        lines = new_rpp_file[:projbay_pos].split('\n')
        lines = [line.lstrip() for line in lines]
        new_rpp_file = '\n'.join(lines) + new_rpp_file[projbay_pos:]

        self.new_rpp_file = new_rpp_file
        new_file_name = f"{self.original_project_name.split('.')[0]}_setlist_{datetime.now().strftime('%d-%m-%Y')}.rpp"
        return self.new_rpp_file, new_file_name
