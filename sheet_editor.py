import gspread
from datetime import date, timedelta
from time import sleep
from setup import logger_setup
logger = logger_setup(__name__)


class SheetEditor:
    def __init__(self):
        logger.info('Connecting to spreadsheet...')
        self.gc = gspread.service_account(filename='service_account.json')
        self.sh = self.gc.open("Weather data")
        logger.info('Connected!')

    def add_day_avgs_for_region(self, region_name, time, avgs):
        if not self.check_if_region_sheet_exists(region_name):
            self.add_new_sheet_for_region(region_name)
        else:
            self.ws = self.sh.worksheet(region_name)

        col = 1
        row = self.get_first_empty_row(region_name)
        adr = self.coords_to_adr(col, row)
        day = date.strftime(time, '%d-%m-%Y')
        content = [[day, avgs[0], avgs[1], avgs[2]]]
        logger.info(f'Updating cell {adr} with: {content}')
        self.update_cell(adr, content)

    def get_first_empty_row(self, region_name):
        values_list = self.sh.worksheet(region_name).col_values(1)
        return len(values_list) + 1

    def check_if_region_sheet_exists(self, region_name):
        worksheet_list = self.sh.worksheets()
        return any(x.title == region_name for x in worksheet_list)

    def add_new_sheet_for_region(self, region_name):
        logger.info(f'Adding new sheet for {region_name}...')
        self.ws = self.sh.add_worksheet(region_name, 1000, 26)
        row = 1
        col = 1
        adr = self.coords_to_adr(col, row)
        self.update_cell(adr, [['Date', 'Day temp', 'Night temp', 'Day and night temp']])
        logger.info(f'Added!')


    def update_cell(self, adr, content):
        while True:
            try:
                self.ws.update(adr, content, raw=True)
                return
            except gspread.exceptions.APIError as e:
                logger.error(e)
                logger.info('Trying again in 5...')
                sleep(5)

    def update_row(self, data, day):
        logger.info(f'Uploading data for {day}')
        row = (day - self.starting_day).days + 2
        logger.debug(f'Updating row: {row}')
        logger.debug(f'Received data: {data}')

        col = 1
        adr = self.coords_to_adr(col, row)
        self.update_cell(adr, date.strftime(day, '%d-%m-%Y'))

        for region in data:
            for number in data[region].values():
                col += 1
                adr = self.coords_to_adr(col, row)
                self.update_cell(adr, number)

    def update_row2(self, data, day):
        logger.info(f'Uploading data for {day}')
        row = (day - self.starting_day).days + 2
        logger.debug(f'Updating row: {row}')
        logger.debug(f'Received data: {data}')

        col = 1
        first_cell = self.coords_to_adr(col, row)
        content = []
        content.append(date.strftime(day, '%d-%m-%Y'))
        #content.append(day)

        for region in data:
            for number in data[region].values():
                col += 1
                content.append(number)

        last_cell = self.coords_to_adr(col, row)
        range = f'{first_cell}:{last_cell}'
        logger.info(f'Updating range: {range}')
        self.update_cell(range, [content])

    def update_header(self, data):
        if not data:
            return

        logger.info(f'Updating header')
        row = 1

        col = 1
        adr = self.coords_to_adr(col, row)
        self.update_cell(adr, 'Date')

        for region in data:
            for category in data[region]:
                col += 1
                adr = self.coords_to_adr(col, row)
                text = region + '\n' + category
                self.update_cell(adr, text)

    def coords_to_adr(self, col, row):
        col_string = ""
        while col > 0:
            col, remainder = divmod(col - 1, 26)
            col_string = chr(65 + remainder) + col_string
        return col_string + str(row)


if __name__ == '__main__':
    sheet_editor = SheetEditor()
    #sheet_editor.add_new_sheet_for_region('AaaAaa')
    print(sheet_editor.get_first_empty_row('AaaA'))