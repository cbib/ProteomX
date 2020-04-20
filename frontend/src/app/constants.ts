export class Constants
{
    static APIConfig = class
    {
        //static APIUrl:string = 'https://services.cbib.u-bordeaux.fr/ProteomiX:4000';
        static APIUrl:string = 'https://services.cbib.u-bordeaux.fr/proteomx/api/';
	static get_api(){
            return this.APIUrl;
        }
    };

}
